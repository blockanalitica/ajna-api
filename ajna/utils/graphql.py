import logging

import requests
from requests.exceptions import ConnectTimeout

log = logging.getLogger(__name__)


class GraphqlClient:
    def __init__(self, endpoint, headers=None, **kwargs):
        self.endpoint = endpoint

    def __request_json(self, query, variables=None):
        json = {"query": query}

        if variables:
            json["variables"] = variables

        return json

    def execute(
        self,
        query,
        variables=None,
    ):
        request_json = self.__request_json(query=query, variables=variables)
        log.debug("Sending request to subgraph %s: %s", self.endpoint, request_json)

        try:
            response = requests.post(self.endpoint, json=request_json, timeout=15)
        except ConnectTimeout:
            log.exception(
                "Subgraph Connection Timeout", extra={"endpoint": self.endpoint}
            )
            return []

        try:
            response.raise_for_status()
        except:  # noqa
            log.exception("Subgraph Exception", extra={"endpoint": self.endpoint})
            return []

        data = response.json()
        if "errors" in data:
            log.error("Subgraph Error", extra={"errors": data["errors"]})
            return []

        return data
