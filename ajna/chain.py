from datetime import datetime
import logging
from django.core.cache import cache
from web3 import Web3
from ajna.metrics import auto_named_statsd_timer

log = logging.getLogger(__name__)


class AjnaChainMixin:
    def get_eoa(self, contract_address):
        abi = [
            {
                "inputs": [],
                "name": "owner",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function",
            },
        ]
        contract = self.eth.contract(
            address=Web3.to_checksum_address(contract_address), abi=abi
        )
        return contract.caller.owner()

    @auto_named_statsd_timer
    def get_block_datetime(self, block_number):
        key = "blocks.{}".format(block_number)
        timestamp = cache.get(key)
        if not timestamp:
            info = self.get_block_info(block_number)
            timestamp = info["timestamp"]
            # Cache timestamp for 1 hour in case some other task requests this block
            cache.set(key, info["timestamp"], 60 * 60)

        return datetime.fromtimestamp(timestamp)

    def get_abi_from_source(self, contract_address):
        # TODO: currently we don't filter by erc721 pools/tokens!
        erc20_pools = self.pool.objects.all().values_list("address", flat=True)
        if contract_address in list(erc20_pools):
            contract_address = self.erc20_pool_default_contract

        return super().get_abi_from_source(contract_address)
