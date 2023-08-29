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

    def get_abi_from_source(self, contract_address):
        # TODO: currently we don't filter by erc721 pools/tokens!
        erc20_pools = self.pool.objects.all().values_list("address", flat=True)
        if contract_address in list(erc20_pools):
            contract_address = self.erc20_pool_default_contract

        return super().get_abi_from_source(contract_address)
