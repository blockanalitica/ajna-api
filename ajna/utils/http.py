import logging

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

log = logging.getLogger(__name__)


def _requests_retry(
    retries=3,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    session=None,
    respect_retry_after_header=True,
):
    """
    Retry backoff: {backoff factor} * (2 ** ({number of total retries} - 1)) seconds.
    It gets applied only after the second attempt! So only 3rd request and after will
    be delayed by [1, 2, 4, ...] seconds respectively if backoff_factor is set to 0.5.
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        respect_retry_after_header=respect_retry_after_header,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def retry_get_json(
    url,
    retries=3,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    session=None,
    respect_retry_after_header=True,
    raise_for_status=True,
    **kwargs,
):
    session = _requests_retry(
        retries=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        session=session,
        respect_retry_after_header=respect_retry_after_header,
    )
    response = session.get(url, **kwargs)
    if raise_for_status:
        response.raise_for_status()

    data = response.json()
    response.close()
    session.close()
    return data
