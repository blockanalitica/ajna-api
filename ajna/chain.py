import logging

from web3 import Web3

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
