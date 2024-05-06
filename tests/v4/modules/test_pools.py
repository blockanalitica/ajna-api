from datetime import datetime

import pytest
from eth_utils import encode_hex
from hexbytes import HexBytes

from ajna.constants import ERC20
from ajna.v4.ethereum.chain import Ethereum
from ajna.v4.modules.pools import PoolERC20Manager


class TestPoolERC20Manager:
    @pytest.mark.django_db
    def test_fetch_and_save_pool_created_events(self, mocker):
        dt = datetime.now()
        dummy_event = {
            "address": "0x6146DD43C5622bB6D12A5240ab9CF4de14eDC625",
            "args": {
                "pool_": "0x866C1DA49A5f311495B11A2bBE83C0fEc81C47C4",
                "subsetHash_": (
                    b'"c\xc47\x8bI \xf0\xbe\xf6\x11\xa3\xff"'
                    b"\xc5\x06\xaf\xa4t[3\x19\xc5\x0bmpJ\x87I\x90\xb8\xb2"
                ),
            },
            "blockHash": HexBytes(
                "0x3221df3d2a75f11d8236a28106e08ec348089e14244af914674429b58f7ecf21"
            ),
            "blockNumber": 19051849,
            "event": "PoolCreated",
            "logIndex": 455,
            "transactionHash": HexBytes(
                "0x2e5df29568efab4edb90468ccfa67494bac0684c2e4e7430d9a6ed84c25ee395"
            ),
            "transactionIndex": 144,
        }
        mocker.patch.object(
            PoolERC20Manager,
            "_fetch_new_pool_created_events",
            return_value=[dummy_event],
        )
        token_created_mock = mocker.patch.object(
            PoolERC20Manager, "_create_erc20_token", return_value=True
        )

        mocker.patch.object(
            Ethereum,
            "multicall",
            return_value={
                "collateralAddress": "0x6123b0049f904d730db3c36a31167d9d4121fa6b",
                "quoteTokenAddress": "0x6b175474e89094c44da98b954eedeac495271d0f",
            },
        )
        mocker.patch.object(Ethereum, "get_block_datetime", return_value=dt)

        chain = Ethereum()

        price_task_mock = mocker.patch.object(
            chain.celery_tasks.fetch_market_price_task, "delay"
        )

        manager = PoolERC20Manager(chain)
        manager.fetch_and_save_pool_created_events()

        assert token_created_mock.call_count == 2
        assert price_task_mock.call_count == 1

        event = chain.pool_event.objects.get(
            pool_address=dummy_event["args"]["pool_"].lower(), name="PoolCreated"
        )

        assert event.block_number == 19051849
        assert event.order_index == "000019051849_000144_000455"
        assert event.block_datetime == dt
        assert (
            event.transaction_hash
            == "0x2e5df29568efab4edb90468ccfa67494bac0684c2e4e7430d9a6ed84c25ee395"
        )

        pool_data = dict(dummy_event["args"])
        pool_data["subsetHash_"] = encode_hex(pool_data["subsetHash_"])
        pool_data["erc"] = ERC20
        pool_data[
            "collateral_token_address"
        ] = "0x6123b0049f904d730db3c36a31167d9d4121fa6b"  # noqa: S105
        pool_data["quote_token_address"] = "0x6b175474e89094c44da98b954eedeac495271d0f"# noqa: S105
        assert event.data == pool_data
