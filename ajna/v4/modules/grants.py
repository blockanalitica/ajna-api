import logging
from decimal import Decimal

from django.core.cache import cache
from eth_abi import abi

from ajna.constants import CHALLENGE_PERIOD_LENGTH, SCREENING_PERIOD_LENGTH
from ajna.utils.utils import compute_order_index
from ajna.utils.wad import wad_to_decimal

log = logging.getLogger(__name__)


def _get_distribution_period_stage(distribution_period, block_number):
    if block_number < distribution_period.start_block + SCREENING_PERIOD_LENGTH:
        return "SCREENING"
    elif (
        block_number > distribution_period.start_block + SCREENING_PERIOD_LENGTH
        and block_number < distribution_period.end_block - CHALLENGE_PERIOD_LENGTH
    ):
        return "FUNDING"
    else:
        return "CHALLENGE"


def _handle_distribution_period_started(chain, event):
    chain.grant_distribution_period.objects.create(
        order_index=event.order_index,
        distribution_id=event.data["distributionId"],
        start_block=event.data["startBlock"],
        end_block=event.data["endBlock"],
        block_datetime=event.block_datetime,
        block_number=event.block_number,
    )


def _handle_proposal_created(chain, event):
    calls = [
        (
            chain.grant_fund_address,
            [
                "getDistributionId()(uint24)",
            ],
            ["getDistributionId", None],
        ),
    ]
    mc_data = chain.multicall(calls, block_identifier=event.block_number)

    distribution_id = mc_data["getDistributionId"]
    distribution_period = chain.grant_distribution_period.objects.get(
        distribution_id=distribution_id
    )

    total_tokens_requested = Decimal("0")
    params = []
    for i, target in enumerate(event.data["targets"]):
        call_data = event.data["calldatas"][i]
        if isinstance(call_data, str):
            call_data = bytes.fromhex(call_data)

        recipient, tokens_requested_wad = abi.decode(["address", "uint256"], call_data[4:])
        tokens_requested = wad_to_decimal(tokens_requested_wad)
        total_tokens_requested += tokens_requested
        params.append(
            {
                "target": target,
                "value": event.data["values"][i],
                "recipient": recipient,
                "tokens_requested": tokens_requested,
            }
        )

    chain.grant_proposal.objects.create(
        order_index=event.order_index,
        proposal_id=event.data["proposalId"],
        distribution_id=distribution_id,
        proposer=event.data["proposer"],
        description=event.data["description"],
        params=params,
        total_tokens_requested=total_tokens_requested,
        block_datetime=event.block_datetime,
        block_number=event.block_number,
        funding_start_block_number=distribution_period.start_block + SCREENING_PERIOD_LENGTH,
        finalize_start_block_number=distribution_period.end_block - CHALLENGE_PERIOD_LENGTH,
    )


def _handle_vote_cast(chain, event):
    proposal = chain.grant_proposal.objects.get(proposal_id=str(event.data["proposalId"]))
    distribution_period = chain.grant_distribution_period.objects.get(
        distribution_id=proposal.distribution_id
    )

    stage = _get_distribution_period_stage(distribution_period, event.block_number)
    match stage:
        case "SCREENING":
            if proposal.screening_votes_received is None:
                proposal.screening_votes_received = Decimal("0")

            proposal.screening_votes_received += wad_to_decimal(event.data["weight"])
            proposal.save()
        case "FUNDING":
            if proposal.funding_votes_received is None:
                proposal.funding_votes_received = Decimal("0")
            if proposal.funding_votes_positive is None:
                proposal.funding_votes_positive = Decimal("0")
            if proposal.funding_votes_negative is None:
                proposal.funding_votes_negative = Decimal("0")

            weight = wad_to_decimal(event.data["weight"])
            if event.data["support"] == 1:
                proposal.funding_votes_received += weight
                proposal.funding_votes_positive += weight
            else:
                proposal.funding_votes_received -= weight
                proposal.funding_votes_negative += abs(weight)
            proposal.save()


def _handle_proposal_executed(chain, event):
    proposal = chain.grant_proposal.objects.get(proposal_id=str(event.data["proposalId"]))
    proposal.executed = True
    proposal.save()


def fetch_and_save_grant_proposals(chain):
    cache_key = "fetch_and_save_grant_proposals.{}.last_block_number".format(chain.unique_key)

    from_block = cache.get(cache_key)
    if not from_block:
        last_event = chain.grant_event.objects.order_by("-order_index").first()
        if last_event:
            from_block = last_event.block_number + 1
        else:
            from_block = chain.grant_fund_start_block

    to_block = chain.get_latest_block()

    events = chain.get_events_for_contract(
        chain.grant_fund_address, from_block=from_block, to_block=to_block
    )

    for raw_event in events:
        order_index = compute_order_index(
            raw_event["blockNumber"],
            raw_event["transactionIndex"],
            raw_event["logIndex"],
        )
        block_datetime = chain.get_block_datetime(raw_event["blockNumber"])
        event = chain.grant_event.objects.create(
            order_index=order_index,
            block_number=raw_event["blockNumber"],
            block_datetime=block_datetime,
            transaction_hash=raw_event["transactionHash"].hex(),
            name=raw_event["event"],
            data=dict(raw_event["args"]),
        )

        match raw_event["event"]:
            case "DistributionPeriodStarted":
                _handle_distribution_period_started(chain, event)
            case "ProposalCreated":
                _handle_proposal_created(chain, event)
            case "VoteCast":
                _handle_vote_cast(chain, event)
            case "VoteCast":
                _handle_proposal_executed(chain, event)

    # Set the block number up to which we've fetch the events so next run we start
    # fetching from this block number. This immensly helps when contract doens't get
    # many events
    cache.set(cache_key, to_block + 1, timeout=None)
