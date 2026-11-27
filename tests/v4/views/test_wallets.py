import pytest

from tests.helpers import generate_ethereum_address

ADDRESS = generate_ethereum_address()
INVALID_BLOCKS = ["notanint", "1); SELECT pg_sleep(3)--", "-1", "9" * 27]


@pytest.mark.django_db
@pytest.mark.parametrize("suffix", ["", "events/", "pools/"])
@pytest.mark.parametrize("block", INVALID_BLOCKS)
def test_wallet_routes_reject_invalid_block(client, suffix, block):
    response = client.get(f"/v4/ethereum/wallets/{ADDRESS}/{suffix}", {"block": block})

    assert response.status_code == 400


@pytest.mark.django_db
def test_wallet_pools_returns_empty_when_no_events_before_block(client):
    response = client.get(f"/v4/ethereum/wallets/{ADDRESS}/pools/", {"block": "1"})

    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.django_db
def test_wallet_events_filters_by_block(client):
    response = client.get(f"/v4/ethereum/wallets/{ADDRESS}/events/", {"block": "1"})

    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.django_db
def test_wallet_returns_404_when_no_events_before_block(client):
    response = client.get(f"/v4/ethereum/wallets/{ADDRESS}/", {"block": "1"})

    assert response.status_code == 404
