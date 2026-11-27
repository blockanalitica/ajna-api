import pytest

from tests.helpers import generate_ethereum_address

ADDRESS = generate_ethereum_address()


@pytest.mark.django_db
@pytest.mark.parametrize("suffix", ["", "events/", "pools/"])
@pytest.mark.parametrize("block", ["notanint", "-1", "9" * 27])
def test_wallet_routes_reject_invalid_block(client, suffix, block):
    response = client.get(f"/v2/ethereum/wallets/{ADDRESS}/{suffix}", {"block": block})

    assert response.status_code == 400
