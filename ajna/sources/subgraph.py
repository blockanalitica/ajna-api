import logging

from django.conf import settings

from ajna.utils.graphql import GraphqlClient

log = logging.getLogger(__name__)


class Subgraph:
    def _fetch_all_with_skip(self, query, key, variables=None, page_size=100):
        """
        NOTE: This should only be used when fetching ALL the data, otherwise it's gonna
        lead to data loss, as id's are not auto incremented but are random bytes
        """
        skip = 0
        if not variables:
            variables = {
                "orderBy": "id",
                "orderDirection": "asc",
            }

        while True:
            variables["first"] = page_size
            variables["skip"] = skip
            results = self.client.execute(query, variables=variables)

            if "data" not in results:
                return None

            data = results["data"][key]
            yield from data

            if len(data) < page_size:
                break
            skip += page_size

    def _fetch_all_by_field(self, query, key, field, value, page_size=1000):
        """
        NOTE: Data loss might occur if using this!

        Below example is explaining if field was "blockNumber" and everything was
        set up for fetching through blockNumber but it's the same for most fields.

        Example: Because we're ordering by block number, multiple rows can be returned for
        the same block number. If we're unfortunate enough, that block number might
        be split over two pages, meaning that in the first page we'll (let's say)
        get 70% of the records, while the other 30% should be on the second page.
        However, because we're using block number to fetch the second page,
        the last block nubmer we'll see is the last from the previous page. We're
        filtering all records by the last block number, so the page will be fetched
        from the last block number from the previous page! Meaning we'll lose the
        30% of records as they will be ignored by the second page.
        """
        while True:
            variables = {
                field: value,
                "first": page_size,
            }

            results = self.client.execute(query, variables=variables)

            if "data" not in results:
                return None

            data = results["data"][key]

            # Don't use `yield from data` to take advantage of orphaned last row
            for row in data:  # noqa: SIM104
                yield row

            if len(data) < page_size:
                break

            log.error(
                "Potential data loss while fetching from subgraph",
                extra={
                    "endpoint": self.client.endpoint,
                    "query": query,
                    "variables": variables,
                },
            )
            # Since we're looping through all data above, we can harness the pythons
            # way of exposing last row from the loop
            value = row[field]

    def tokens(self):
        query = """
            query (
              $first: Int, $skip: Int, $orderBy: Token_orderBy,
              $orderDirection: OrderDirection, $filter: Token_filter
            ) {
              tokens(
                first: $first
                skip: $skip
                orderBy: $orderBy
                orderDirection: $orderDirection
                where: $filter
              ) {
                id
                symbol
                name
                decimals
                isERC721
                poolCount
                totalSupply
                txCount
              }
            }
        """
        yield from self._fetch_all_with_skip(query, "tokens")

    def pools(self):
        query = """
            query (
              $first: Int, $skip: Int, $orderBy: Pool_orderBy,
              $orderDirection: OrderDirection, $filter: Pool_filter
            ) {
              pools(
                first: $first
                skip: $skip
                orderBy: $orderBy
                orderDirection: $orderDirection
                where: $filter
              ) {
                id
                createdAtBlockNumber
                createdAtTimestamp
                collateralToken {
                  id
                  symbol
                  name
                  decimals
                  isERC721
                  poolCount
                  totalSupply
                  txCount
                }
                quoteToken {
                  id
                  symbol
                  name
                  decimals
                  isERC721
                  poolCount
                  totalSupply
                  txCount
                }
                poolSize
                t0debt
                inflator
                borrowRate
                lendRate
                borrowFeeRate
                depositFeeRate
                pledgedCollateral
                totalInterestEarned
                txCount
                loansCount
                maxBorrower
                hpb
                hpbIndex
                htp
                htpIndex
                lup
                lupIndex
                momp
                reserves
                claimableReserves
                claimableReservesRemaining
                burnEpoch
                totalAjnaBurned
                minDebtAmount
                actualUtilization
                targetUtilization
                totalBondEscrowed
                quoteTokenBalance
                collateralBalance
              }
            }
        """
        yield from self._fetch_all_with_skip(query, "pools")

    def buckets(self):
        query = """
            query (
              $first: Int, $skip: Int, $orderBy: Bucket_orderBy,
              $orderDirection: OrderDirection, $filter: Bucket_filter
            ) {
              buckets(
                first: $first
                skip: $skip
                orderBy: $orderBy
                orderDirection: $orderDirection
                where: $filter
              ) {
                id
                bucketIndex
                bucketPrice
                exchangeRate
                poolAddress
                collateral
                deposit
                lpb
              }
            }
        """
        yield from self._fetch_all_with_skip(query, "buckets", page_size=500)

    def remove_collaterals(self, block_number):
        query = """
            query fetchRemoveCollaterals($blockNumber: BigInt!) {
              removeCollaterals(
                orderBy: blockNumber
                orderDirection: asc
                where: {blockNumber_gt: $blockNumber}
              ) {
                amount
                blockNumber
                blockTimestamp
                claimer
                index
                lpRedeemed
                transactionHash
                pool {
                  id
                  collateralToken {
                    id
                  }
                  quoteToken {
                    id
                  }
                }
                bucket {
                  bucketIndex
                }
              }
            }
        """
        results = self.client.execute(query, variables={"blockNumber": block_number})
        return results["data"]["removeCollaterals"]

    def add_collaterals(self, block_number):
        query = """
            query ($blockNumber: BigInt!, $first: Int){
              addCollaterals(
                first: $first
                orderBy: blockNumber
                orderDirection: asc
                where: {blockNumber_gt: $blockNumber}
              ) {
                blockNumber
                actor
                amount
                blockTimestamp
                bucket {
                  bucketIndex
                }
                index
                lpAwarded
                transactionHash
                pool {
                  id
                  collateralToken {
                    id
                  }
                  quoteToken {
                    id
                  }
                }
              }
            }
        """
        yield from self._fetch_all_by_field(
            query, "addCollaterals", "blockNumber", block_number
        )

    def add_quote_tokens(self, block_number):
        query = """
            query ($blockNumber: BigInt!, $first: Int){
              addQuoteTokens(
                first: $first
                orderBy: blockNumber
                orderDirection: asc
                where: {blockNumber_gt: $blockNumber}
              ) {
                id
                transactionHash
                pool {
                  id
                  collateralToken {
                    id
                  }
                  quoteToken {
                    id
                  }
                  depositFeeRate
                }
                lup
                lpAwarded
                lender
                index
                blockTimestamp
                blockNumber
                amount
                bucket {
                  bucketIndex
                  bucketPrice
                }
              }
            }
        """
        yield from self._fetch_all_by_field(
            query, "addQuoteTokens", "blockNumber", block_number
        )

    def remove_quote_tokens(self, block_number):
        query = """
            query ($blockNumber: BigInt!, $first: Int){
              removeQuoteTokens(
                first: $first
                orderBy: blockNumber
                orderDirection: asc
                where: {blockNumber_gt: $blockNumber}
              ) {
                amount
                blockNumber
                blockTimestamp
                bucket {
                  bucketIndex
                }
                id
                index
                lender
                lpRedeemed
                lup
                transactionHash
                pool {
                  id
                  collateralToken {
                    id
                  }
                  quoteToken {
                    id
                  }
                }
              }
            }
        """
        yield from self._fetch_all_by_field(
            query, "removeQuoteTokens", "blockNumber", block_number
        )

    def draw_debts(self, block_number):
        query = """
            query ($blockNumber: BigInt!, $first: Int){
              drawDebts(
                first: $first
                orderBy: blockNumber
                orderDirection: asc
                where: {blockNumber_gt: $blockNumber}
              ) {
                amountBorrowed
                blockNumber
                blockTimestamp
                borrower
                collateralPledged
                id
                lup
                pool {
                  id
                  collateralToken {
                    id
                  }
                  quoteToken {
                    id
                  }
                  borrowFeeRate
                }
                transactionHash
              }
            }
        """
        yield from self._fetch_all_by_field(
            query, "drawDebts", "blockNumber", block_number
        )

    def repay_debts(self, block_number):
        query = """
            query ($blockNumber: BigInt!, $first: Int){
              repayDebts(
                first: $first
                orderBy: blockNumber
                orderDirection: asc
                where: {blockNumber_gt: $blockNumber}
              ) {
                id
                blockNumber
                blockTimestamp
                borrower
                lup
                collateralPulled
                quoteRepaid
                transactionHash
                pool {
                  id
                  collateralToken {
                    id
                  }
                  quoteToken {
                    id
                  }
                }
              }
            }
        """
        yield from self._fetch_all_by_field(
            query, "repayDebts", "blockNumber", block_number
        )

    def settled_liquidation_auctions(self, settle_time):
        query = """
            query ($settleTime: BigInt!, , $first: Int) {
              liquidationAuctions(
                first: $first
                orderBy: settleTime
                orderDirection: asc
                where: {settleTime_gt: $settleTime, settled: true}
              ) {
                id
                settled
                settleTime
                neutralPrice
                kicker
                kickTime
                debt
                debtRemaining
                collateral
                collateralRemaining
                borrower
                bondSize
                bondFactor
                lastTakePrice
                pool {
                  id
                  collateralToken {
                    id
                    symbol
                  }
                  quoteToken {
                    id
                    symbol
                  }
                }
              }
            }
        """
        yield from self._fetch_all_by_field(
            query, "liquidationAuctions", "settleTime", settle_time
        )

    def active_liquidation_auctions(self):
        query = """
            query (
              $first: Int, $skip: Int, $orderBy: LiquidationAuction_orderBy,
              $orderDirection: OrderDirection, $filter: LiquidationAuction_filter
            ) {
              liquidationAuctions(
                first: $first
                skip: $skip
                orderBy: $orderBy
                orderDirection: $orderDirection
                where: {settled: false}
              ) {
                id
                settled
                settleTime
                neutralPrice
                kicker
                kickTime
                debt
                debtRemaining
                collateral
                collateralRemaining
                borrower
                bondSize
                bondFactor
                lastTakePrice
                pool {
                  id
                  collateralToken {
                    id
                  }
                  quoteToken {
                    id
                  }
                }
              }
            }
        """
        yield from self._fetch_all_with_skip(
            query, "liquidationAuctions", page_size=1000
        )


class GoerliSubgraph(Subgraph):
    def __init__(self):
        self.client = GraphqlClient(endpoint=settings.SUBGRAPH_ENDPOINT_GOERLI)


class EthereumSubgraph(Subgraph):
    def __init__(self):
        self.client = GraphqlClient(endpoint=settings.SUBGRAPH_ENDPOINT_MAINNET)
