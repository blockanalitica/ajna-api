import pytest


@pytest.mark.django_db
@pytest.mark.parametrize("days_ago", ["9" * 30, "-" + "9" * 30])
def test_history_rejects_out_of_range_days_ago(client, days_ago):
    response = client.get("/v4/ethereum/stats/history/", {"days_ago": days_ago})

    assert response.status_code == 400
