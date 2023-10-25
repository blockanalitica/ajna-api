import logging
from datetime import datetime

from web3 import Web3
from web3.exceptions import ContractLogicError

from ajna.constants import ERC20

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
            try:
                address = contract.caller.owner()
            except ContractLogicError:
                log.error("Can't find owner (EOA) of %s contract", contract_address)

        return address.lower()

    def load_abi(self, contract_address, abi_name=None):
        contract_address = contract_address.lower()
        try:
            pool = self.pool.objects.get(address=contract_address)
        except self.pool.DoesNotExist:
            pass
        else:
            if pool.erc == ERC20:
                contract_address = self.erc20_pool_abi_contract
            else:
                contract_address = self.erc721_pool_abi_contract
        return super().load_abi(contract_address, abi_name=abi_name)

    def get_block_datetime(self, block_number):
        global BLOCK_DATETIMES

        if block_number not in BLOCK_DATETIMES:
            block_info = self.get_block_info(block_number)
            BLOCK_DATETIMES[block_number] = datetime.fromtimestamp(
                block_info["timestamp"]
            )

        return BLOCK_DATETIMES[block_number]
