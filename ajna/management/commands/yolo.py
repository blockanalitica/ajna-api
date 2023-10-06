from django.core.management.base import BaseCommand
from django.db import connection

from ajna.v1.goerli.chain import MODEL_MAP
from ajna.v2.ethereum.chain import Ethereum
from datetime import datetime
from ajna.v2.modules.events import _create_notification


class Command(BaseCommand):
    def handle(self, *args, **options):
        chain = Ethereum()
        quote_token_price = 6768689
        order_index = 234567654
        block_datetime = datetime.now()
        event = {
            "args": {
                "borrower": "0x3758301013393f133a5f0B2F677A7000E4A6A66c",
                "amountBorrowed": 1644000000000000000000,
                "collateralPledged": 386100000000000000,
                "lup": 17251100121621363478270,
            },
            "event": "DrawDebt",
            "logIndex": 60,
            "transactionIndex": 36,
            "address": "0xdB30a08Ebc49af1BaF87f57824f85056cEd33d5F",
            "blockNumber": 18102835,
        }
        pool_event = chain.pool_event(
            pool_address="0xdB30a08Ebc49af1BaF87f57824f85056cEd33d5F".lower(),
            # wallet_addresses=_get_wallet_addresses(event),
            block_number=18102835,
            block_datetime=block_datetime,
            order_index=order_index,
            transaction_hash="3476769036739046",
            name="DrawDebt",
            data=dict(event["args"]),
            # collateral_token_price=collateral_token_price,
            quote_token_price=quote_token_price,
        )

        _create_notification(chain, pool_event)
