import pytest
from django.urls import reverse

from tests.v1.factories import V1GrantProposalFactory


@pytest.mark.django_db
def test_grants_funding_proposals(client, monkeypatch):
    current_block = 9500000
    monkeypatch.setattr(
        "ajna.chain.Blockchain.get_latest_block", lambda x: current_block
    )

    V1GrantProposalFactory(
        funding_start_block_number=9000000,
        finalize_start_block_number=9510000,
        end_block=9520000,
        screening_votes_received=400,
        description={"title": "1"},
    )
    V1GrantProposalFactory(
        funding_start_block_number=9499999,
        finalize_start_block_number=9510000,
        end_block=9520000,
        description={"title": "2"},
        screening_votes_received=300,
    )
    V1GrantProposalFactory(
        funding_start_block_number=9500000,
        finalize_start_block_number=9510000,
        end_block=9520000,
        description={"title": "3"},
        screening_votes_received=666,
    )
    # Funding starts in the future
    V1GrantProposalFactory(
        funding_start_block_number=9555555,
        finalize_start_block_number=9510000,
        end_block=9520000,
        description={"title": "4"},
    )
    # Already in finalize stage
    V1GrantProposalFactory(
        funding_start_block_number=9000000,
        finalize_start_block_number=9499999,
        end_block=9520000,
        description={"title": "5"},
    )
    V1GrantProposalFactory(
        funding_start_block_number=9000000,
        finalize_start_block_number=9500000,
        end_block=9520000,
        description={"title": "6"},
    )

    # Already ended
    V1GrantProposalFactory(
        funding_start_block_number=9000000,
        finalize_start_block_number=9510000,
        end_block=9499999,
        description={"title": "7"},
    )
    V1GrantProposalFactory(
        funding_start_block_number=9000000,
        finalize_start_block_number=9510000,
        end_block=9500000,
        description={"title": "8"},
    )

    response = client.get(
        reverse(
            "v1_ethereum:grands-funding-proposals",
        )
    )

    assert response.status_code == 200
    proposals = response.data
    assert len(proposals) == 3
    assert proposals[0]["title"] == "3"
    assert proposals[1]["title"] == "1"
    assert proposals[2]["title"] == "2"


@pytest.mark.django_db
def test_grants_finalize_proposals(client, monkeypatch):
    current_block = 9500000
    monkeypatch.setattr(
        "ajna.chain.Blockchain.get_latest_block", lambda x: current_block
    )
    V1GrantProposalFactory(
        finalize_start_block_number=9499999,
        end_block=9520000,
        description={"title": "1"},
        funding_votes_received=300,
    )
    V1GrantProposalFactory(
        finalize_start_block_number=9500000,
        end_block=9520000,
        description={"title": "2"},
        funding_votes_received=400,
    )
    # Finalize in the future
    V1GrantProposalFactory(
        finalize_start_block_number=9500001,
        end_block=9520000,
        description={"title": "3"},
    )
    # Already ended
    V1GrantProposalFactory(
        finalize_start_block_number=9510000,
        end_block=9499999,
        description={"title": "4"},
    )
    V1GrantProposalFactory(
        finalize_start_block_number=9510000,
        end_block=9500000,
        description={"title": "5"},
    )

    response = client.get(
        reverse(
            "v1_ethereum:grands-finalize-proposals",
        )
    )

    assert response.status_code == 200
    proposals = response.data
    assert len(proposals) == 2
    assert proposals[0]["title"] == "2"
    assert proposals[1]["title"] == "1"
