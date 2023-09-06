from datetime import datetime

from ajna.utils.utils import compute_order_index


def fetch_new_pools(chain):
    last_event = chain.pool_event.objects.all().order_by("-order_index").first()

    from_block_number = chain.erc20_pool_factory_block_number

    if last_event:
        from_block_number = last_event.block_number + 1

    events = chain.get_events_for_contract_topics(
        chain.erc20_pool_factory_address,
        ["0x83a48fbcfc991335314e74d0496aab6a1987e992ddc85dddbcc4d6dd6ef2e9fc"],
        from_block_number,
    )
    for event in events:
        order_index = compute_order_index(
            event["blockNumber"], event["transactionIndex"], event["logIndex"]
        )
        block_info = chain.get_block_info(event["blockNumber"])
        block_datetime = datetime.fromtimestamp(block_info["timestamp"])
        chain.pool_event.objects.create(
            pool_address=event["args"]["pool_"].lower(),
            block_number=event["blockNumber"],
            block_datetime=block_datetime,
            order_index=order_index,
            transaction_hash=event["transactionHash"].hex(),
            name=event["event"],
            data=dict(event["args"]),
        )
