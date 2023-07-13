from decimal import Decimal

import pytest
import responses
from django.conf import settings

from ajna.sources.subgraph import GoerliSubgraph
from ajna.v1.ethereum import models
from ajna.v1.modules.events import (
    fetch_and_save_add_collaterals,
    fetch_and_save_add_quote_tokens,
    fetch_and_save_draw_debts,
    fetch_and_save_remove_collaterals,
    fetch_and_save_remove_quote_tokens,
    fetch_and_save_repay_debts,
)


@responses.activate
@pytest.mark.django_db
def test_fetch_and_save_remove_collaterals(mocker):
    """
    Test fetch_and_save_remove_collaterals function to ensure proper data fetching and saving.

    This test checks that the fetch_and_save_remove_collaterals function:
    1. Fetches removeCollaterals data from the mocked Subgraph API.
    2. Creates and saves RemoveCollateral instances in the database.
    """
    # Mock the subgraph.remove_collaterals() call

    mocker.patch("ajna.v1.modules.events._get_price", return_value=None)
    mock_data = {
        "data": {
            "removeCollaterals": [
                {
                    "amount": "12345.555",
                    "blockNumber": "8783138",
                    "blockTimestamp": "1680775044",
                    "claimer": "0x147a247bef72ecfa3738f85ccb31b34f180fffff",
                    "index": "123",
                    "lpRedeemed": "123.419041377711846637",
                    "transactionHash": (
                        "0x03b89471e80376e56ab5590c75dd6198339e245170b93129e161b3c888b46153"
                    ),
                    "pool": {
                        "id": "0x147a247bef72ecfa3738f85ccb31b34f180ffa4e",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                    },
                    "bucket": {"bucketIndex": "2168"},
                },
                {
                    "amount": "6.6",
                    "blockNumber": "8783138",
                    "blockTimestamp": "1680775044",
                    "claimer": "0x147a247bef72ecfa3738f85ccb31b34f180feeee",
                    "index": "124",
                    "lpRedeemed": "0.419041377711846632",
                    "transactionHash": (
                        "0x03b89471e80376e56ab5590c75dd6198339e245170b93129e161b3c888b46153"
                    ),
                    "pool": {
                        "id": "0x147a247bef72ecfa3738f85ccb31b34f180ffa4e",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                    },
                    "bucket": {"bucketIndex": "2168"},
                },
            ]
        }
    }
    responses.add(
        responses.POST,
        settings.SUBGRAPH_ENDPOINT_GOERLI,
        json=mock_data,
        status=200,
    )
    model = models.V1EthereumRemoveCollateral
    price_model = models.V1EthereumPriceFeed
    subgraph = GoerliSubgraph()
    # Run the fetch_and_save_remove_collaterals function
    fetch_and_save_remove_collaterals(subgraph, model, price_model, 8783137)

    results = model.objects.all().order_by("index")
    assert len(results) == 2
    assert results[0].amount == Decimal("12345.555")
    assert (
        results[0].transaction_hash
        == "0x03b89471e80376e56ab5590c75dd6198339e245170b93129e161b3c888b46153"
    )
    assert results[0].claimer == "0x147a247bef72ecfa3738f85ccb31b34f180fffff"
    assert results[0].index == 123

    assert results[1].amount == Decimal("6.6")
    assert (
        results[1].transaction_hash
        == "0x03b89471e80376e56ab5590c75dd6198339e245170b93129e161b3c888b46153"
    )
    assert results[1].claimer == "0x147a247bef72ecfa3738f85ccb31b34f180feeee"
    assert results[1].index == 124


@pytest.mark.django_db
def test_fetch_and_save_add_collaterals(mocker):
    """
    Test fetch_and_save_add_collaterals function to ensure proper data fetching and saving.

    This test checks that the fetch_and_save_remove_collaterals function:
    1. Fetches removeCollaterals data from the mocked Subgraph API.
    2. Creates and saves AddCollateral instances in the database.
    """
    # Mock the subgraph.add_collaterals() call
    mocker.patch("ajna.v1.modules.events._get_price", return_value=None)
    mock_data = {
        "data": {
            "addCollaterals": [
                {
                    "amount": "12345.555",
                    "blockNumber": "8783138",
                    "blockTimestamp": "1680775044",
                    "actor": "0x147a247bef72ecfa3738f85ccb31b34f180fffff",
                    "index": "123",
                    "lpAwarded": "123.419041377711846637",
                    "transactionHash": (
                        "0x03b89471e80376e56ab5590c75dd6198339e245170b93129e161b3c888b46153"
                    ),
                    "pool": {
                        "id": "0x147a247bef72ecfa3738f85ccb31b34f180ffa4e",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                    },
                    "bucket": {"bucketIndex": "2168"},
                },
                {
                    "amount": "6.6",
                    "blockNumber": "8783138",
                    "blockTimestamp": "1680775044",
                    "actor": "0x147a247bef72ecfa3738f85ccb31b34f180feeee",
                    "index": "124",
                    "lpAwarded": "0.419041377711846632",
                    "transactionHash": (
                        "0x03b89471e80376e56ab5590c75dd6198339e245170b93129e161b3c888b46153"
                    ),
                    "pool": {
                        "id": "0x147a247bef72ecfa3738f85ccb31b34f180ffa4e",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                    },
                    "bucket": {"bucketIndex": "2168"},
                },
            ]
        }
    }
    responses.add(
        responses.POST,
        settings.SUBGRAPH_ENDPOINT_GOERLI,
        json=mock_data,
        status=200,
    )
    model = models.V1EthereumAddCollateral
    price_model = models.V1EthereumPriceFeed
    subgraph = GoerliSubgraph()
    # Run the fetch_and_save_add_collaterals function
    fetch_and_save_add_collaterals(subgraph, model, price_model, 8783137)

    results = model.objects.all().order_by("index")
    assert len(results) == 2
    assert results[0].amount == Decimal("12345.555")
    assert (
        results[0].transaction_hash
        == "0x03b89471e80376e56ab5590c75dd6198339e245170b93129e161b3c888b46153"
    )
    assert results[0].actor == "0x147a247bef72ecfa3738f85ccb31b34f180fffff"
    assert results[0].index == 123

    assert results[1].amount == Decimal("6.6")
    assert (
        results[1].transaction_hash
        == "0x03b89471e80376e56ab5590c75dd6198339e245170b93129e161b3c888b46153"
    )
    assert results[1].actor == "0x147a247bef72ecfa3738f85ccb31b34f180feeee"
    assert results[1].index == 124


@responses.activate
@pytest.mark.django_db
def test_fetch_and_save_add_quote_tokens(mocker):
    """
    Test fetch_and_save_add_quote_tokens function to ensure proper data fetching and saving.

    This test checks that the fetch_and_save_add_quote_tokens function:
    1. Fetches removeCollaterals data from the mocked Subgraph API.
    2. Creates and saves AddQuoteToken instances in the database.
    """
    # Mock the subgraph.add_quote_tokens() call
    mocker.patch("ajna.v1.modules.events._get_price", return_value=None)
    mock_data = {
        "data": {
            "addQuoteTokens": [
                {
                    "transactionHash": (
                        "0x03b89471e80376e56ab5590c75dd6198339e245170b93129e161b3c888b46153"
                    ),
                    "pool": {
                        "id": "0xe1200aefd60559d494d4419e17419571ef8fc1eb",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                        "depositFeeRate": "0.0025",
                    },
                    "lup": "861.020873502022238541",
                    "lpAwarded": "700",
                    "lender": "0xc14b54ce5171d73fb9402bd038b2b0363e0dbe24",
                    "index": 2801,
                    "blockTimestamp": "1680775044",
                    "blockNumber": "8783138",
                    "amount": "700",
                    "bucket": {"bucketIndex": 2801, "bucketPrice": 1},
                },
                {
                    "transactionHash": (
                        "0x12eae2469d0f95f56ff90c2f3be6f3e59716694022076a090f3bc715cfcec241"
                    ),
                    "pool": {
                        "id": "0xe1200aefd60559d494d4419e17419571ef8fc1eb",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                        "depositFeeRate": "0.0025",
                    },
                    "lup": "12662.543981384068647567",
                    "lpAwarded": "99.984095379886831965",
                    "lender": "0x5dbf920561e0579f518e07d7a495597d8496f544",
                    "index": 2299,
                    "blockTimestamp": "1678965528",
                    "blockNumber": "8664528",
                    "amount": "99.9841871232876712",
                    "bucket": {"bucketIndex": 2299, "bucketPrice": 1},
                },
            ]
        }
    }
    responses.add(
        responses.POST,
        settings.SUBGRAPH_ENDPOINT_GOERLI,
        json=mock_data,
        status=200,
    )
    model = models.V1EthereumAddQuoteToken
    price_model = models.V1EthereumPriceFeed
    subgraph = GoerliSubgraph()
    # Run the fetch_and_save_add_quote_tokens function
    fetch_and_save_add_quote_tokens(subgraph, model, price_model, 0)

    results = model.objects.all().order_by("-index")
    assert len(results) == 2
    assert results[0].amount == Decimal("700")
    assert (
        results[0].transaction_hash
        == "0x03b89471e80376e56ab5590c75dd6198339e245170b93129e161b3c888b46153"
    )
    assert results[0].lender == "0xc14b54ce5171d73fb9402bd038b2b0363e0dbe24"
    assert results[0].index == 2801

    assert results[1].amount == Decimal("99.9841871232876712")
    assert (
        results[1].transaction_hash
        == "0x12eae2469d0f95f56ff90c2f3be6f3e59716694022076a090f3bc715cfcec241"
    )
    assert results[1].lender == "0x5dbf920561e0579f518e07d7a495597d8496f544"
    assert results[1].index == 2299


@responses.activate
@pytest.mark.django_db
def test_fetch_and_save_remove_quote_tokens(mocker):
    """
    Test fetch_and_save_remove_quote_tokens function to ensure proper data fetching and saving.

    This test checks that the fetch_and_save_add_quote_tokens function:
    1. Fetches removeCollaterals data from the mocked Subgraph API.
    2. Creates and saves RemoveQuoteToken instances in the database.
    """
    # Mock the subgraph.remove_quote_tokens() call
    mocker.patch("ajna.v1.modules.events._get_price", return_value=None)
    mock_data = {
        "data": {
            "removeQuoteTokens": [
                {
                    "amount": "100",
                    "blockNumber": "8632034",
                    "blockTimestamp": "1678475556",
                    "bucket": {"bucketIndex": 2261},
                    "index": 2261,
                    "lender": "0x4ee82c30cc8d1f38381950b35f7a73ba3028ba6e",
                    "lpRedeemed": "99.999980460353187479",
                    "lup": "20135.606256843391129786",
                    "transactionHash": (
                        "0x013c31cd6f493c281468d141a3d49dec940bd8474c19ed650bef03597c2795af"
                    ),
                    "pool": {
                        "id": "0x17e5a1a6450d4fb32fffc329ca92db55293db10e",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                    },
                },
                {
                    "amount": "200.000408596072242625",
                    "blockNumber": "8824713",
                    "blockTimestamp": "1681413612",
                    "bucket": {"bucketIndex": 2168},
                    "index": 2168,
                    "lender": "0x4ee82c30cc8d1f38381950b35f7a73ba3028ba6e",
                    "lpRedeemed": "199.859943962768069259",
                    "lup": "20236.284288127607921848",
                    "transactionHash": (
                        "0x11e42394b1d0f7fceddb32458038d9929d3539ee5db8d97807d0c0c3655b904a"
                    ),
                    "pool": {
                        "id": "0x17e5a1a6450d4fb32fffc329ca92db55293db10e",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                    },
                },
            ]
        }
    }
    responses.add(
        responses.POST,
        settings.SUBGRAPH_ENDPOINT_GOERLI,
        json=mock_data,
        status=200,
    )
    model = models.V1EthereumRemoveQuoteToken
    price_model = models.V1EthereumPriceFeed
    subgraph = GoerliSubgraph()
    # Run the fetch_and_save_remove_quote_tokens function
    fetch_and_save_remove_quote_tokens(subgraph, model, price_model, 0)

    results = model.objects.all().order_by("-index")
    assert len(results) == 2
    assert results[0].amount == Decimal("100")
    assert (
        results[0].transaction_hash
        == "0x013c31cd6f493c281468d141a3d49dec940bd8474c19ed650bef03597c2795af"
    )
    assert results[0].lender == "0x4ee82c30cc8d1f38381950b35f7a73ba3028ba6e"
    assert results[0].index == 2261

    assert results[1].amount == Decimal("200.000408596072242625")
    assert (
        results[1].transaction_hash
        == "0x11e42394b1d0f7fceddb32458038d9929d3539ee5db8d97807d0c0c3655b904a"
    )
    assert results[1].lender == "0x4ee82c30cc8d1f38381950b35f7a73ba3028ba6e"
    assert results[1].index == 2168


@responses.activate
@pytest.mark.django_db
def test_fetch_and_save_draw_debts(mocker):
    """
    Test fetch_and_save_draw_debts function to ensure proper data fetching and saving.

    This test checks that the fetch_and_save_draw_debts function:
    1. Fetches removeCollaterals data from the mocked Subgraph API.
    2. Creates and saves DrawDebt instances in the database.
    """
    # Mock the subgraph.draw_debts() call
    mocker.patch("ajna.v1.modules.events._get_price", return_value=None)
    mock_data = {
        "data": {
            "drawDebts": [
                {
                    "amountBorrowed": "100",
                    "blockNumber": "8619505",
                    "blockTimestamp": "1678290552",
                    "borrower": "0xa7eb5e0c25c1547db026ef86ec825dd763e0cb47",
                    "collateralPledged": "0.01",
                    "id": "1",
                    "lup": "20135.606256843391129786",
                    "pool": {
                        "id": "0x17e5a1a6450d4fb32fffc329ca92db55293db10e",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                        "borrowFeeRate": "1",
                    },
                    "transactionHash": (
                        "0xbf063810e0cc74eb389481d3626045ba31829fde93795b0894983943123f47e9"
                    ),
                },
                {
                    "amountBorrowed": "200",
                    "blockNumber": "8658504",
                    "blockTimestamp": "1678872864",
                    "borrower": "0xe015ec6dd822b865316065201cc827e7521ab6d8",
                    "collateralPledged": "1",
                    "id": "2",
                    "lup": "12662.543981384068647567",
                    "pool": {
                        "id": "0xe1200aefd60559d494d4419e17419571ef8fc1eb",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                        "borrowFeeRate": "1",
                    },
                    "transactionHash": (
                        "0xb9ed3a59264d92fc4e0347d7de61fc854c06fdd1b505168198bf2a27cf3299ee"
                    ),
                },
            ]
        }
    }
    responses.add(
        responses.POST,
        settings.SUBGRAPH_ENDPOINT_GOERLI,
        json=mock_data,
        status=200,
    )
    model = models.V1EthereumDrawDebt
    price_model = models.V1EthereumPriceFeed
    subgraph = GoerliSubgraph()
    # Run the fetch_and_save_draw_debts function
    fetch_and_save_draw_debts(subgraph, model, price_model, 0)

    results = model.objects.all().order_by("block_number")
    assert len(results) == 2
    assert results[0].amount_borrowed == Decimal("100")
    assert (
        results[0].transaction_hash
        == "0xbf063810e0cc74eb389481d3626045ba31829fde93795b0894983943123f47e9"
    )
    assert results[0].borrower == "0xa7eb5e0c25c1547db026ef86ec825dd763e0cb47"

    assert results[1].amount_borrowed == Decimal("200")
    assert (
        results[1].transaction_hash
        == "0xb9ed3a59264d92fc4e0347d7de61fc854c06fdd1b505168198bf2a27cf3299ee"
    )
    assert results[1].borrower == "0xe015ec6dd822b865316065201cc827e7521ab6d8"


@responses.activate
@pytest.mark.django_db
def test_fetch_and_save_repay_debts(mocker):
    """
    Test fetch_and_save_repay_debts function to ensure proper data fetching and saving.

    This test checks that the fetch_and_save_repay_debts function:
    1. Fetches removeCollaterals data from the mocked Subgraph API.
    2. Creates and saves RepayDebt instances in the database.
    """
    # Mock the subgraph.repay_debts() call
    mocker.patch("ajna.v1.modules.events._get_price", return_value=None)
    mock_data = {
        "data": {
            "repayDebts": [
                {
                    "blockNumber": "8626074",
                    "blockTimestamp": "1678387872",
                    "borrower": "0xa7eb5e0c25c1547db026ef86ec825dd763e0cb47",
                    "lup": "20135.606256843391129786",
                    "collateralPulled": "0.00001",
                    "quoteRepaid": "0",
                    "id": "1",
                    "transactionHash": (
                        "0x79a506e8c4466cb4b912ffb691a676f9c31c27c071bfbb670343cb836a807de8"
                    ),
                    "pool": {
                        "id": "0x17e5a1a6450d4fb32fffc329ca92db55293db10e",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                    },
                },
                {
                    "blockNumber": "8669809",
                    "blockTimestamp": "1679046240",
                    "borrower": "0xe015ec6dd822b865316065201cc827e7521ab6d8",
                    "lup": "12662.543981384068647567",
                    "collateralPulled": "0.0000000000001",
                    "quoteRepaid": "0",
                    "id": "2",
                    "transactionHash": (
                        "0xf2a8b85947c71fdc7237544a443e13cbf1eacfd922d2f4c6d45cce34402d88bc"
                    ),
                    "pool": {
                        "id": "0xe1200aefd60559d494d4419e17419571ef8fc1eb",
                        "collateralToken": {
                            "id": "0x6b175474e89094c44da98b954eedeac495271d0f"
                        },
                        "quoteToken": {
                            "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                        },
                    },
                },
            ]
        }
    }
    responses.add(
        responses.POST,
        settings.SUBGRAPH_ENDPOINT_GOERLI,
        json=mock_data,
        status=200,
    )
    model = models.V1EthereumRepayDebt
    price_model = models.V1EthereumPriceFeed
    subgraph = GoerliSubgraph()
    # Run the fetch_and_save_repay_debts function
    fetch_and_save_repay_debts(subgraph, model, price_model, 0)

    results = model.objects.all().order_by("block_number")
    assert len(results) == 2
    assert results[0].collateral_pulled == Decimal("0.00001")
    assert (
        results[0].transaction_hash
        == "0x79a506e8c4466cb4b912ffb691a676f9c31c27c071bfbb670343cb836a807de8"
    )
    assert results[0].borrower == "0xa7eb5e0c25c1547db026ef86ec825dd763e0cb47"

    assert results[1].collateral_pulled == Decimal("0.0000000000001")
    assert (
        results[1].transaction_hash
        == "0xf2a8b85947c71fdc7237544a443e13cbf1eacfd922d2f4c6d45cce34402d88bc"
    )
    assert results[1].borrower == "0xe015ec6dd822b865316065201cc827e7521ab6d8"
