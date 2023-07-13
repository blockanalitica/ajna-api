from decimal import Decimal

import pytest
import responses
from django.conf import settings

from ajna.sources.subgraph import GoerliSubgraph
from ajna.v1.ethereum import models
from ajna.v1.modules.pools import (
    fetch_and_save_buckets,
    fetch_and_save_pool_data,
    update_token_prices,
)
from tests.v1.factories import V1TokenFactory


@pytest.mark.skip(reason="needs refactoring")
@responses.activate
@pytest.mark.django_db
def test_fetch_and_save_pool_data():
    """
    Test fetch_and_save_pool_data function to ensure proper data fetching and saving.

    This test checks that the fetch_and_save_pool_data function:
    1. Fetches pool data from the mocked Subgraph API.
    2. Creates and saves Pool instances in the database.
    3. Creates and saves Token instances in the database when a new pool is created.
    4. Creates and saves PoolSnapshot instances in the database if the snapshot argument is True.
    """
    # Mock the subgraph.pools() call
    mock_pools_data = {
        "data": {
            "pools": [
                {
                    "id": "0x147a247bef72ecfa3738f85ccb31b34f180ffa4e",
                    "createdAtBlockNumber": "8614160",
                    "createdAtTimestamp": "1678210668",
                    "collateralToken": {
                        "id": "0x9c09fe6b19174d838cae2c4fb5a4a311c4008441",
                        "symbol": "TWETH",
                        "name": "TestWrappedETH",
                        "decimals": "18",
                        "isERC721": False,
                        "poolCount": "1",
                        "totalSupply": "100001000000000000000000000",
                        "txCount": "4",
                    },
                    "quoteToken": {
                        "id": "0x10aa0cf12aab305bd77ad8f76c037e048b12513b",
                        "symbol": "TDAI",
                        "name": "TestDai",
                        "decimals": "18",
                        "isERC721": False,
                        "poolCount": "1",
                        "totalSupply": "101000000000000000000000000",
                        "txCount": "7",
                    },
                    "borrowFeeRate": "0.000000001678210668",
                    "currentDebt": "150.123998394665979436",
                    "inflator": "1",
                    "inflatorUpdate": "1678210668",
                    "interestRate": "0.04293",
                    "pledgedCollateral": "0.096521568553805922",
                    "totalInterestEarned": "0",
                    "txCount": "6",
                    "poolSize": "300",
                    "loansCount": "1",
                    "maxBorrower": "0xd25e48b4a9b89f0715c2bca66a33a5fdef77ac25",
                    "pendingInflator": "1.000001078151266135",
                    "pendingInterestFactor": "1.000001078151266135",
                    "hpb": "2020.273840569605963251",
                    "hpbIndex": 2630,
                    "htp": "1555.339793869750954343",
                    "htpIndex": 2682,
                    "lup": "2010.222726934931322934",
                    "lupIndex": 2631,
                    "momp": "0",
                    "reserves": "0.12383653846153845",
                    "claimableReserves": "0",
                    "claimableReservesRemaining": "0",
                    "reserveAuctionPrice": "0",
                    "reserveAuctionTimeRemaining": "0",
                    "burnEpoch": "0",
                    "totalAjnaBurned": "0",
                    "minDebtAmount": "15.012399839466597944",
                    "collateralization": "1.292463915304048312",
                    "actualUtilization": "0.745927103540257088",
                    "targetUtilization": "0.773715157544378701",
                    "totalBondEscrowed": "0",
                },
                {
                    "id": "0x17e5a1a6450d4fb32fffc329ca92db55293db10e",
                    "createdAtBlockNumber": "8614101",
                    "createdAtTimestamp": "1678209804",
                    "collateralToken": {
                        "id": "0x7ccf0411c7932b99fc3704d68575250f032e3bb7",
                        "symbol": "WBTC",
                        "name": "",
                        "decimals": "8",
                        "isERC721": False,
                        "poolCount": "1",
                        "totalSupply": "50000000000000",
                        "txCount": "53",
                    },
                    "quoteToken": {
                        "id": "0x6fb5ef893d44f4f88026430d82d4ef269543cb23",
                        "symbol": "USDC",
                        "name": "",
                        "decimals": "6",
                        "isERC721": False,
                        "poolCount": "1",
                        "totalSupply": "5000000000000000",
                        "txCount": "115",
                    },
                    "borrowFeeRate": "0.000000001678209804",
                    "currentDebt": "111.367008512438020267",
                    "inflator": "1",
                    "inflatorUpdate": "1678209804",
                    "interestRate": "0.020533285917",
                    "pledgedCollateral": "0.02999",
                    "totalInterestEarned": "0",
                    "txCount": "86",
                    "poolSize": "395.419041304911846637",
                    "loansCount": "3",
                    "maxBorrower": "0x35ac4c93054cda212ee7d7d036f88370f35a46b8",
                    "pendingInflator": "1.003530001934220344",
                    "pendingInterestFactor": "1",
                    "hpb": "20236.284288127607921848",
                    "hpbIndex": 2168,
                    "htp": "9566.869131442162670511",
                    "htpIndex": 2318,
                    "lup": "20236.284288127607921848",
                    "lupIndex": 2168,
                    "momp": "20236.284288127607921848",
                    "reserves": "0.61208820752617363",
                    "claimableReserves": "0.055253164963983529",
                    "claimableReservesRemaining": "0",
                    "reserveAuctionPrice": "0",
                    "reserveAuctionTimeRemaining": "0",
                    "burnEpoch": "0",
                    "totalAjnaBurned": "0",
                    "minDebtAmount": "3.712233617081267342",
                    "collateralization": "5.449425048830030097",
                    "actualUtilization": "0.268995730311937234",
                    "targetUtilization": "0.455161801430039856",
                    "totalBondEscrowed": "0",
                },
                {
                    "id": "0x9fbbf73dd76ea1159cf44afe6cdfefc9225bd182",
                    "createdAtBlockNumber": "8767380",
                    "createdAtTimestamp": "1680536496",
                    "collateralToken": {
                        "id": "0xb4fbf271143f4fbf7b91a5ded31805e42b2208d6",
                        "symbol": "WETH",
                        "name": "Wrapped Ether",
                        "decimals": "18",
                        "isERC721": False,
                        "poolCount": "1",
                        "totalSupply": "1171366546484577318637104",
                        "txCount": "45",
                    },
                    "quoteToken": {
                        "id": "0x10aa0cf12aab305bd77ad8f76c037e048b12513b",
                        "symbol": "TDAI",
                        "name": "TestDai",
                        "decimals": "18",
                        "isERC721": False,
                        "poolCount": "1",
                        "totalSupply": "101000000000000000000000000",
                        "txCount": "7",
                    },
                    "borrowFeeRate": "0.000000001680536496",
                    "currentDebt": "0",
                    "inflator": "1",
                    "inflatorUpdate": "1680536496",
                    "interestRate": "0.05",
                    "pledgedCollateral": "0",
                    "totalInterestEarned": "0",
                    "txCount": "3",
                    "poolSize": "300",
                    "loansCount": "0",
                    "maxBorrower": "0x0000000000000000000000000000000000000000",
                    "pendingInflator": "1",
                    "pendingInterestFactor": "1",
                    "hpb": "2010.222726934931322934",
                    "hpbIndex": 2631,
                    "htp": "0",
                    "htpIndex": 7388,
                    "lup": "1004968987.606512354182109771",
                    "lupIndex": 0,
                    "momp": "0",
                    "reserves": "0",
                    "claimableReserves": "0",
                    "claimableReservesRemaining": "0",
                    "reserveAuctionPrice": "0",
                    "reserveAuctionTimeRemaining": "0",
                    "burnEpoch": "0",
                    "totalAjnaBurned": "0",
                    "minDebtAmount": "0",
                    "collateralization": "1",
                    "actualUtilization": "0",
                    "targetUtilization": "1",
                    "totalBondEscrowed": "0",
                },
                {
                    "id": "0xe1200aefd60559d494d4419e17419571ef8fc1eb",
                    "createdAtBlockNumber": "8614134",
                    "createdAtTimestamp": "1678210296",
                    "collateralToken": {
                        "id": "0xb4fbf271143f4fbf7b91a5ded31805e42b2208d6",
                        "symbol": "WETH",
                        "name": "Wrapped Ether",
                        "decimals": "18",
                        "isERC721": False,
                        "poolCount": "1",
                        "totalSupply": "1171366546484577318637104",
                        "txCount": "45",
                    },
                    "quoteToken": {
                        "id": "0x6fb5ef893d44f4f88026430d82d4ef269543cb23",
                        "symbol": "USDC",
                        "name": "",
                        "decimals": "6",
                        "isERC721": False,
                        "poolCount": "1",
                        "totalSupply": "5000000000000000",
                        "txCount": "115",
                    },
                    "borrowFeeRate": "0.000000001678210296",
                    "currentDebt": "1003.346860645241410405",
                    "inflator": "1",
                    "inflatorUpdate": "1678210296",
                    "interestRate": "0.0504024726447",
                    "pledgedCollateral": "11.39999999999968",
                    "totalInterestEarned": "0",
                    "txCount": "68",
                    "poolSize": "4704.200845272195929329",
                    "loansCount": "3",
                    "maxBorrower": "0xc929ad814edee51574ba929e2fee5ad2b2c8ecfe",
                    "pendingInflator": "1.007386934796807053",
                    "pendingInterestFactor": "1",
                    "hpb": "11290.197689748004267623",
                    "hpbIndex": 2285,
                    "htp": "303.923640355460423251",
                    "htpIndex": 3009,
                    "lup": "861.020873502022238541",
                    "lupIndex": 2801,
                    "momp": "932.546868736522759726",
                    "reserves": "15.520874193225691441",
                    "claimableReserves": "10.504139889999484389",
                    "claimableReservesRemaining": "1.021873179819789635",
                    "reserveAuctionPrice": "0",
                    "reserveAuctionTimeRemaining": "0",
                    "burnEpoch": "1",
                    "totalAjnaBurned": "0",
                    "minDebtAmount": "33.444895354841380347",
                    "collateralization": "9.782895968409616987",
                    "actualUtilization": "0.216826657361504323",
                    "targetUtilization": "0.424454107203042893",
                    "totalBondEscrowed": "0",
                },
            ]
        }
    }
    subgraph_pools_url = settings.SUBGRAPH_ENDPOINT_GOERLI
    responses.add(
        responses.POST,
        subgraph_pools_url,
        json=mock_pools_data,
        status=200,
    )
    pool_model = models.V1EthereumPool
    token_model = models.V1EthereumToken
    pool_snapshot_model = models.V1EthereumPoolSnapshot

    # Run the fetch_and_save_pool_data function
    fetch_and_save_pool_data(pool_model, token_model, pool_snapshot_model)

    # Test that the pools are saved in the database
    assert pool_model.objects.count() == 4
    assert pool_model.objects.filter(
        address="0x147a247bef72ecfa3738f85ccb31b34f180ffa4e"
    ).exists()
    assert pool_model.objects.filter(
        address="0x17e5a1a6450d4fb32fffc329ca92db55293db10e"
    ).exists()
    assert pool_model.objects.filter(
        address="0xe1200aefd60559d494d4419e17419571ef8fc1eb"
    ).exists()

    # Test that the tokens and snapshots are saved in the database
    assert token_model.objects.count() == 5
    assert pool_snapshot_model.objects.count() == 4


@pytest.mark.skip(reason="needs refactoring")
@responses.activate
@pytest.mark.django_db
def test_fetch_and_save_pool_data__no_snapshot():
    """
    Test fetch_and_save_pool_data function to ensure proper data fetching and saving.

    This test checks that the fetch_and_save_pool_data function:
    1. Fetches pool data from the mocked Subgraph API.
    2. Creates and saves Pool instances in the database.
    3. Creates and saves Token instances in the database when a new pool is created.
    4. Do not create PoolSnapshot instances in the database
    """
    # Mock the subgraph.pools() call
    mock_pools_data = {
        "data": {
            "pools": [
                {
                    "id": "0x147a247bef72ecfa3738f85ccb31b34f180ffa4e",
                    "createdAtBlockNumber": "8614160",
                    "createdAtTimestamp": "1678210668",
                    "collateralToken": {
                        "id": "0x9c09fe6b19174d838cae2c4fb5a4a311c4008441",
                        "symbol": "TWETH",
                        "name": "TestWrappedETH",
                        "decimals": "18",
                        "isERC721": False,
                        "poolCount": "1",
                        "totalSupply": "100001000000000000000000000",
                        "txCount": "4",
                    },
                    "quoteToken": {
                        "id": "0x10aa0cf12aab305bd77ad8f76c037e048b12513b",
                        "symbol": "TDAI",
                        "name": "TestDai",
                        "decimals": "18",
                        "isERC721": False,
                        "poolCount": "1",
                        "totalSupply": "101000000000000000000000000",
                        "txCount": "7",
                    },
                    "borrowFeeRate": "0.000000001678210668",
                    "currentDebt": "150.123998394665979436",
                    "inflator": "1",
                    "inflatorUpdate": "1678210668",
                    "interestRate": "0.04293",
                    "pledgedCollateral": "0.096521568553805922",
                    "totalInterestEarned": "0",
                    "txCount": "6",
                    "poolSize": "300",
                    "loansCount": "1",
                    "maxBorrower": "0xd25e48b4a9b89f0715c2bca66a33a5fdef77ac25",
                    "pendingInflator": "1.000001078151266135",
                    "pendingInterestFactor": "1.000001078151266135",
                    "hpb": "2020.273840569605963251",
                    "hpbIndex": 2630,
                    "htp": "1555.339793869750954343",
                    "htpIndex": 2682,
                    "lup": "2010.222726934931322934",
                    "lupIndex": 2631,
                    "momp": "0",
                    "reserves": "0.12383653846153845",
                    "claimableReserves": "0",
                    "claimableReservesRemaining": "0",
                    "reserveAuctionPrice": "0",
                    "reserveAuctionTimeRemaining": "0",
                    "burnEpoch": "0",
                    "totalAjnaBurned": "0",
                    "minDebtAmount": "15.012399839466597944",
                    "collateralization": "1.292463915304048312",
                    "actualUtilization": "0.745927103540257088",
                    "targetUtilization": "0.773715157544378701",
                    "totalBondEscrowed": "0",
                },
            ]
        }
    }
    subgraph_pools_url = settings.SUBGRAPH_ENDPOINT_GOERLI
    responses.add(
        responses.POST,
        subgraph_pools_url,
        json=mock_pools_data,
        status=200,
    )
    pool_model = models.V1EthereumPool
    token_model = models.V1EthereumToken
    pool_snapshot_model = models.V1EthereumPoolSnapshot

    # Run the fetch_and_save_pool_data function
    fetch_and_save_pool_data(
        pool_model, token_model, pool_snapshot_model, snapshot=False
    )

    # Test that the pools are saved in the database
    assert pool_model.objects.count() == 1
    assert pool_model.objects.filter(
        address="0x147a247bef72ecfa3738f85ccb31b34f180ffa4e"
    ).exists()

    # Test that the tokens are saved and snapshots are not saved in the database
    assert token_model.objects.count() == 2
    assert pool_snapshot_model.objects.count() == 0


@pytest.mark.django_db
@responses.activate
def test_fetch_and_save_buckets():
    """
    Test fetch_and_save_buckets function to ensure proper data fetching and saving.

    This test checks that the fetch_and_save_buckets function:
    1. Fetches bucket data from the mocked Subgraph API.
    2. Creates and saves Bucket instances in the database, updating existing ones if needed.

    """
    # Mock the subgraph.buckets() call
    mock_buckets_data = {
        "data": {
            "buckets": [
                {
                    "bucketIndex": "1",
                    "bucketPrice": "100",
                    "collateral": "0",
                    "exchangeRate": "1",
                    "id": "0x16",
                    "lpb": "300",
                    "poolAddress": "0x1",
                    "deposit": "300",
                },
                {
                    "bucketIndex": "2",
                    "bucketPrice": "100",
                    "collateral": "0",
                    "exchangeRate": "2",
                    "id": "0x17",
                    "lpb": "300",
                    "poolAddress": "0x1",
                    "deposit": "300",
                },
                {
                    "bucketIndex": "1",
                    "bucketPrice": "100",
                    "collateral": "0",
                    "exchangeRate": "1",
                    "id": "0x18",
                    "lpb": "300",
                    "poolAddress": "0x2",
                    "deposit": "300",
                },
                # update
                {
                    "bucketIndex": "2",
                    "bucketPrice": "100",
                    "collateral": "0",
                    "exchangeRate": "3",
                    "id": "0x17",
                    "lpb": "300",
                    "poolAddress": "0x1",
                    "deposit": "300",
                },
            ]
        }
    }

    external_api_url = settings.SUBGRAPH_ENDPOINT_GOERLI
    responses.add(
        responses.POST,
        external_api_url,
        json=mock_buckets_data,
        status=200,
    )

    bucket_model = models.V1EthereumBucket
    subgraph = GoerliSubgraph()
    fetch_and_save_buckets(subgraph, bucket_model)

    assert bucket_model.objects.count() == 3

    assert bucket_model.objects.filter(bucket_index=1, pool_address="0x1").exists()
    bucket_0 = bucket_model.objects.get(bucket_index=1, pool_address="0x1")
    assert bucket_0.exchange_rate == 1.0
    assert bucket_0.collateral == 0
    assert bucket_0.deposit == 300
    assert bucket_0.lpb == 300
    assert bucket_0.bucket_price == 100

    assert bucket_model.objects.filter(bucket_index=2, pool_address="0x1").exists()
    bucket_1 = bucket_model.objects.get(bucket_index=2, pool_address="0x1")
    assert bucket_1.exchange_rate == 3.0
    assert bucket_1.collateral == 0
    assert bucket_1.deposit == 300
    assert bucket_1.lpb == 300
    assert bucket_1.bucket_price == 100

    assert bucket_model.objects.filter(bucket_index=1, pool_address="0x2").exists()
    bucket_2 = bucket_model.objects.get(bucket_index=1, pool_address="0x2")
    assert bucket_2.exchange_rate == 1.0
    assert bucket_2.collateral == 0
    assert bucket_2.deposit == 300
    assert bucket_2.lpb == 300
    assert bucket_2.bucket_price == 100


@pytest.mark.django_db
@responses.activate
def test_update_token_prices():
    """
    Test update_token_prices function to ensure proper updating of underlying_price.

    This test checks that the update_token_prices function:
    1. Fetches the current prices for tokens from the mocked API.
    2. Updates the underlying_price field for all Token instances in the database.
    """

    # Create tokens using the TokenFactory
    token_1 = V1TokenFactory()
    token_2 = V1TokenFactory()
    token_3 = V1TokenFactory()

    # Mock response for get_current_prices
    mock_response = {
        "coins": {
            f"ethereum:{token_1.underlying_address}": {
                "decimals": 6,
                "symbol": f"{token_1.symbol}",
                "price": 1,
                "timestamp": 1680029580,
                "confidence": 0.99,
            },
            f"ethereum:{token_2.underlying_address}": {
                "decimals": 18,
                "symbol": f"{token_2.symbol}",
                "price": 1000,
                "timestamp": 1680029580,
                "confidence": 0.99,
            },
            f"ethereum:{token_3.underlying_address}": {
                "decimals": 18,
                "symbol": f"{token_3.symbol}",
                "price": 0.089,
                "timestamp": 1680029580,
                "confidence": 0.99,
            },
        }
    }
    token_model = models.V1EthereumToken
    price_feed_model = models.V1EthereumPriceFeed
    addresses = token_model.objects.all().values_list("underlying_address", flat=True)
    coins = [f"ethereum:{address}" for address in addresses]
    external_api_url = "https://coins.llama.fi/prices/current/{}/".format(
        ",".join(coins)
    )
    responses.add(
        responses.GET,
        external_api_url,
        json=mock_response,
        status=200,
        content_type="application/json",
    )

    update_token_prices(token_model, price_feed_model)

    # Assert that the underlying_price field has been updated for tokens
    assert token_model.objects.get(
        underlying_address=token_1.underlying_address
    ).underlying_price == Decimal("1")
    assert token_model.objects.get(
        underlying_address=token_2.underlying_address
    ).underlying_price == Decimal("1000")
    assert token_model.objects.get(
        underlying_address=token_3.underlying_address
    ).underlying_price == Decimal("0.089")

    assert price_feed_model.objects.count() == 3
