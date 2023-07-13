from datetime import datetime, timedelta

from ajna.constants import BLOCKS_PER_MINUTE


def get_block_number(chain, days_ago, calculated=False):
    if calculated:
        latest_block = chain.get_latest_block()
        block_number = int(latest_block - BLOCKS_PER_MINUTE * 60 * 24 * days_ago)
    else:
        dt = datetime.now() - timedelta(days=days_ago)
        block = chain.block.objects.filter(datetime__lte=dt).latest()
        block_number = block.block_number

    return block_number
