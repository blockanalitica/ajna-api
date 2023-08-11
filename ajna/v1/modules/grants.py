import json
import logging
from decimal import Decimal

from ajna.constants import CHALLENGE_PERIOD_LENGTH, SCREENING_PERIOD_LENGTH

log = logging.getLogger(__name__)


def fetch_and_save_grant_proposals_data(chain, subgraph):
    current_block = chain.get_latest_block()
    end_block_number = current_block - 7200  # Get already ended blocks in the last
    # day to update most recent ones

    proposals = subgraph.grant_proposals(end_block_number)

    for proposal in proposals:
        if not proposal["distribution"]:
            # If istribution is missing, it's most likely that the proposal was
            # created outside of the ajna dapp and for now we don't trust it
            log.error(
                "Proposal doesn't have a distribution", extra={"proposal": proposal}
            )
            continue

        start_block = int(proposal["distribution"]["startBlock"])
        end_block = int(proposal["distribution"]["endBlock"])

        chain.grant_proposal.objects.update_or_create(
            uid=proposal["proposalId"],
            defaults={
                "description": json.loads(proposal["description"]),
                "executed": proposal["executed"],
                "screening_votes_received": Decimal(proposal["screeningVotesReceived"]),
                "funding_votes_received": Decimal(proposal["fundingVotesReceived"]),
                "total_tokens_requested": Decimal(proposal["totalTokensRequested"]),
                "start_block": start_block,
                "end_block": end_block,
                "funding_start_block_number": start_block + SCREENING_PERIOD_LENGTH,
                "finalize_start_block_number": end_block - CHALLENGE_PERIOD_LENGTH,
            },
        )
