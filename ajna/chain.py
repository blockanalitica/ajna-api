import logging

import requests
from multicall import Call, Multicall
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from web3 import Web3

log = logging.getLogger(__name__)


class Blockchain:
    def __init__(
        self,
        node=None,
        _web3=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._node_address = node
        self._web3 = _web3
        self._abis = {}

    @property
    def web3(self):
        if not self._web3:
            session = requests.Session()
            retries = 3
            retry = Retry(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=0.5,
                status_forcelist=(429,),
                respect_retry_after_header=True,
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            self._web3 = Web3(
                Web3.HTTPProvider(
                    self._node_address, request_kwargs={"timeout": 60}, session=session
                )
            )
        return self._web3

    @property
    def eth(self):
        return self.web3.eth

    def get_block_info(self, block_number):
        return self.eth.get_block(block_number)

    def get_latest_block(self):
        return self.eth.blockNumber

    def call_multicall(self, calls, block_id=None):
        multicalls = []
        for address, function, response in calls:
            multicalls.append(Call(address, function, [response]))

        multi = Multicall(multicalls, _w3=self.web3, block_id=block_id)

        return multi()

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
            address=Web3.toChecksumAddress(contract_address), abi=abi
        )
        return contract.caller.owner()
