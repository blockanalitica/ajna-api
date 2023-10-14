import logging
from datetime import datetime

from web3 import Web3

log = logging.getLogger(__name__)


BLOCK_DATETIMES = {}


class AjnaChainMixin:
    def get_eoa(self, contract_address):
        address = Web3.to_checksum_address(contract_address)
        code = self.eth.get_code(address).hex()
        if len(code) > 2:
            abi = [
                {
                    "inputs": [],
                    "name": "owner",
                    "outputs": [
                        {"internalType": "address", "name": "", "type": "address"}
                    ],
                    "stateMutability": "view",
                    "type": "function",
                },
            ]
            contract = self.eth.contract(
                address=Web3.to_checksum_address(contract_address), abi=abi
            )
            address = contract.caller.owner()

        return address.lower()

    def get_abi_from_source(self, contract_address):
        # TODO: currently we don't filter by erc721 pools/tokens!
        erc20_pools = self.pool.objects.all().values_list("address", flat=True)
        if contract_address in list(erc20_pools):
            contract_address = self.erc20_pool_abi_contract

        return super().get_abi_from_source(contract_address)

    def get_block_datetime(self, block_number):
        global BLOCK_DATETIMES

        if block_number not in BLOCK_DATETIMES:
            block_info = self.get_block_info(block_number)
            BLOCK_DATETIMES[block_number] = datetime.fromtimestamp(
                block_info["timestamp"]
            )

        return BLOCK_DATETIMES[block_number]
