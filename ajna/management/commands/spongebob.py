from datetime import datetime
from collections import defaultdict
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import connection

from ajna.utils.db import fetch_all
from ajna.utils.utils import wad_to_decimal
from ajna.v1.modules.events import fetch_and_save_events_for_pool
from ajna.v1.ethereum.chain import Ethereum, EthereumModels
from ajna.v1.goerli.chain import Goerli
from ajna.v1.modules.positions import _handle_debt_events, save_wallet_positions
from ajna.v1.ethereum.tasks import fetch_and_save_events_task
from ajna.v1.goerli import tasks


# def _get_addresses_from_events(chain):
#     sql = """
#         SELECT DISTINCT
#               x.wallet_address
#         FROM (
#             SELECT DISTINCT
#                  dd.borrower AS wallet_address
#             FROM {draw_debt_table} AS dd
#             WHERE dd.block_number >= %s

#             UNION

#             SELECT DISTINCT
#                 rd.borrower AS wallet_address
#             FROM {repay_debt_table} rd
#             WHERE rd.block_number >= %s

#             UNION

#             SELECT DISTINCT
#                 aqt.lender AS wallet_address
#             FROM {add_quote_token_table} AS aqt
#             WHERE aqt.block_number >= %s

#             UNION

#             SELECT DISTINCT
#                 rqt.lender AS wallet_address
#             FROM {remove_quote_token_table} rqt
#             WHERE rqt.block_number >= %s

#             UNION

#             SELECT DISTINCT
#                 mqt.lender AS wallet_address
#             FROM {move_quote_token_table} mqt
#             WHERE mqt.block_number >= %s

#             UNION

#             SELECT
#                 ac.actor AS wallet_address
#             FROM {add_collateral_table} AS ac
#             WHERE ac.block_number >= %s

#             UNION

#             SELECT
#                 rc.claimer AS wallet_address
#             FROM {remove_collateral_table} rc
#             WHERE rc.block_number >= %s
#         ) x
#     """.format(
#         draw_debt_table=chain.draw_debt._meta.db_table,
#         repay_debt_table=chain.repay_debt._meta.db_table,
#         add_quote_token_table=chain.add_quote_token._meta.db_table,
#         remove_quote_token_table=chain.remove_quote_token._meta.db_table,
#         move_quote_token_table=chain.move_quote_token._meta.db_table,
#         add_collateral_table=chain.add_collateral._meta.db_table,
#         remove_collateral_table=chain.remove_collateral._meta.db_table,
#     )
#     with connection.cursor() as cursor:
#         cursor.execute(sql, [0] * 7)
#         addresses = fetch_all(cursor)

#     return set(a["wallet_address"] for a in addresses)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # chain = Goerli()
        # chain.pool_event.objects.all().delete()
        # chain = Ethereum()
        # chain.pool_event.objects.all().delete()
        tasks.fetch_and_save_events_task()
        # fetch_and_save_events_task()
        # chain.pool_event.objects.all().delete()

        
        # fetch_and_save_events_for_pool(
        #     chain, "0x0d4a28e6afa37d5e28a5db21fed14135921c432e", 9540642
        # )
        # chain.burek()

        # contract = chain.get_contract("0x0d4a28e6afa37d5e28a5db21fed14135921c432e")

        # bla = contract.events.IncreaseLPAllowance.create_filter(fromBlock=0)
        # print(bla.get_all_entries())


# [
#     AttributeDict(
#         {
#             "args": AttributeDict(
#                 {
#                     "lender": "0x298F06C6259585300d9EF273Ff3Cf3117460070a",
#                     "transferors": ["0x23E2EFF19bd50BfCF0364B7dCA01004D5cce41f9"],
#                 }
#             ),
#             "event": "ApproveLPTransferors",
#             "logIndex": 2,
#             "transactionIndex": 2,
#             "transactionHash": HexBytes(
#                 "0x86830b7ffec4fbee1775edafdd0ef1951e9c5052c1c31d3be3e9b1a51396bb5e"
#             ),
#             "address": "0x0D4a28e6AFa37D5E28A5DB21fED14135921C432e",
#             "blockHash": HexBytes(
#                 "0x1efed4aafea91c40229f26203cf016f8148c4c9bc8bdf801c1020bfbd1aea0a7"
#             ),
#             "blockNumber": 9563217,
#         }
#     )
# ]
# chain.burek()


# chain.

# chain = Ethereum()

# sql = """
# SELECT DISTINCT name
# FROM {pool_event_table}
# """.format(
#     pool_event_table=chain.pool_event._meta.db_table
# )

# with connection.cursor() as cursor:
#     cursor.execute(sql, [])
#     bla = fetch_all(cursor)
# print(bla)

# chain.pool_event.objects.all().delete()
# fetch_and_save_events_task()

# fetch_and_save_events_for_pool(chain, "0x15838515903b3843e02f9283b4492833f138e8de")


{
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "address",
            "name": "owner",
            "type": "address",
        },
        {
            "indexed": True,
            "internalType": "address",
            "name": "spender",
            "type": "address",
        },
        {
            "indexed": False,
            "internalType": "uint256[]",
            "name": "indexes",
            "type": "uint256[]",
        },
        {
            "indexed": False,
            "internalType": "uint256[]",
            "name": "amounts",
            "type": "uint256[]",
        },
    ],
    "name": "IncreaseLPAllowance",
    "type": "event",
}

# [
#     {"inputs": [], "name": "AllowanceAlreadySet", "type": "error"},
#     {"inputs": [], "name": "AlreadyInitialized", "type": "error"},
#     {"inputs": [], "name": "AmountLTMinDebt", "type": "error"},
#     {"inputs": [], "name": "AuctionActive", "type": "error"},
#     {"inputs": [], "name": "AuctionNotClearable", "type": "error"},
#     {"inputs": [], "name": "AuctionNotCleared", "type": "error"},
#     {"inputs": [], "name": "AuctionNotCleared", "type": "error"},
#     {"inputs": [], "name": "AuctionPriceGtBucketPrice", "type": "error"},
#     {"inputs": [], "name": "BorrowerNotSender", "type": "error"},
#     {"inputs": [], "name": "BorrowerOk", "type": "error"},
#     {"inputs": [], "name": "BorrowerUnderCollateralized", "type": "error"},
#     {"inputs": [], "name": "BucketBankruptcyBlock", "type": "error"},
#     {"inputs": [], "name": "BucketIndexOutOfBounds", "type": "error"},
#     {"inputs": [], "name": "CannotMergeToHigherPrice", "type": "error"},
#     {"inputs": [], "name": "DustAmountNotExceeded", "type": "error"},
#     {"inputs": [], "name": "FlashloanCallbackFailed", "type": "error"},
#     {"inputs": [], "name": "FlashloanIncorrectBalance", "type": "error"},
#     {"inputs": [], "name": "FlashloanUnavailableForToken", "type": "error"},
#     {"inputs": [], "name": "InsufficientCollateral", "type": "error"},
#     {"inputs": [], "name": "InsufficientLP", "type": "error"},
#     {"inputs": [], "name": "InsufficientLiquidity", "type": "error"},
#     {"inputs": [], "name": "InvalidAllowancesInput", "type": "error"},
#     {"inputs": [], "name": "InvalidAmount", "type": "error"},
#     {"inputs": [], "name": "InvalidIndex", "type": "error"},
#     {"inputs": [], "name": "LUPBelowHTP", "type": "error"},
#     {"inputs": [], "name": "LUPGreaterThanTP", "type": "error"},
#     {"inputs": [], "name": "LimitIndexExceeded", "type": "error"},
#     {"inputs": [], "name": "MoveToSameIndex", "type": "error"},
#     {"inputs": [], "name": "NoAllowance", "type": "error"},
#     {"inputs": [], "name": "NoAuction", "type": "error"},
#     {"inputs": [], "name": "NoClaim", "type": "error"},
#     {"inputs": [], "name": "NoDebt", "type": "error"},
#     {"inputs": [], "name": "NoReserves", "type": "error"},
#     {"inputs": [], "name": "NoReservesAuction", "type": "error"},
#     {"inputs": [], "name": "PRBMathSD59x18__DivInputTooSmall", "type": "error"},
#     {
#         "inputs": [{"internalType": "uint256", "name": "rAbs", "type": "uint256"}],
#         "name": "PRBMathSD59x18__DivOverflow",
#         "type": "error",
#     },
#     {
#         "inputs": [{"internalType": "int256", "name": "x", "type": "int256"}],
#         "name": "PRBMathSD59x18__Exp2InputTooBig",
#         "type": "error",
#     },
#     {
#         "inputs": [{"internalType": "int256", "name": "x", "type": "int256"}],
#         "name": "PRBMathSD59x18__FromIntOverflow",
#         "type": "error",
#     },
#     {
#         "inputs": [{"internalType": "int256", "name": "x", "type": "int256"}],
#         "name": "PRBMathSD59x18__FromIntUnderflow",
#         "type": "error",
#     },
#     {
#         "inputs": [{"internalType": "int256", "name": "x", "type": "int256"}],
#         "name": "PRBMathSD59x18__LogInputTooSmall",
#         "type": "error",
#     },
#     {"inputs": [], "name": "PRBMathSD59x18__MulInputTooSmall", "type": "error"},
#     {
#         "inputs": [{"internalType": "uint256", "name": "rAbs", "type": "uint256"}],
#         "name": "PRBMathSD59x18__MulOverflow",
#         "type": "error",
#     },
#     {
#         "inputs": [{"internalType": "int256", "name": "x", "type": "int256"}],
#         "name": "PRBMathSD59x18__SqrtNegativeInput",
#         "type": "error",
#     },
#     {
#         "inputs": [{"internalType": "int256", "name": "x", "type": "int256"}],
#         "name": "PRBMathSD59x18__SqrtOverflow",
#         "type": "error",
#     },
#     {
#         "inputs": [{"internalType": "uint256", "name": "prod1", "type": "uint256"}],
#         "name": "PRBMath__MulDivFixedPointOverflow",
#         "type": "error",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "prod1", "type": "uint256"},
#             {"internalType": "uint256", "name": "denominator", "type": "uint256"},
#         ],
#         "name": "PRBMath__MulDivOverflow",
#         "type": "error",
#     },
#     {"inputs": [], "name": "PoolUnderCollateralized", "type": "error"},
#     {"inputs": [], "name": "PriceBelowLUP", "type": "error"},
#     {"inputs": [], "name": "RemoveDepositLockedByAuctionDebt", "type": "error"},
#     {"inputs": [], "name": "RemoveDepositLockedByAuctionDebt", "type": "error"},
#     {"inputs": [], "name": "ReserveAuctionTooSoon", "type": "error"},
#     {"inputs": [], "name": "TakeNotPastCooldown", "type": "error"},
#     {"inputs": [], "name": "TransactionExpired", "type": "error"},
#     {"inputs": [], "name": "TransactionExpired", "type": "error"},
#     {"inputs": [], "name": "TransferToSameOwner", "type": "error"},
#     {"inputs": [], "name": "TransferorNotApproved", "type": "error"},
#     {"inputs": [], "name": "ZeroThresholdPrice", "type": "error"},
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "actor",
#                 "type": "address",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "uint256",
#                 "name": "index",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "amount",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lpAwarded",
#                 "type": "uint256",
#             },
#         ],
#         "name": "AddCollateral",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "lender",
#                 "type": "address",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "uint256",
#                 "name": "index",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "amount",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lpAwarded",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lup",
#                 "type": "uint256",
#             },
#         ],
#         "name": "AddQuoteToken",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "lender",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "address[]",
#                 "name": "transferors",
#                 "type": "address[]",
#             },
#         ],
#         "name": "ApproveLPTransferors",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "borrower",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "collateral",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lp",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "index",
#                 "type": "uint256",
#             },
#         ],
#         "name": "AuctionNFTSettle",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "borrower",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "collateral",
#                 "type": "uint256",
#             },
#         ],
#         "name": "AuctionSettle",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "kicker",
#                 "type": "address",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "reciever",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "amount",
#                 "type": "uint256",
#             },
#         ],
#         "name": "BondWithdrawn",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "uint256",
#                 "name": "index",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lpForfeited",
#                 "type": "uint256",
#             },
#         ],
#         "name": "BucketBankruptcy",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "borrower",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "index",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "amount",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "collateral",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "bondChange",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "bool",
#                 "name": "isReward",
#                 "type": "bool",
#             },
#         ],
#         "name": "BucketTake",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "taker",
#                 "type": "address",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "kicker",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lpAwardedTaker",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lpAwardedKicker",
#                 "type": "uint256",
#             },
#         ],
#         "name": "BucketTakeLPAwarded",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "owner",
#                 "type": "address",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "spender",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256[]",
#                 "name": "indexes",
#                 "type": "uint256[]",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256[]",
#                 "name": "amounts",
#                 "type": "uint256[]",
#             },
#         ],
#         "name": "DecreaseLPAllowance",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "borrower",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "amountBorrowed",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "collateralPledged",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lup",
#                 "type": "uint256",
#             },
#         ],
#         "name": "DrawDebt",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "receiver",
#                 "type": "address",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "token",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "amount",
#                 "type": "uint256",
#             },
#         ],
#         "name": "Flashloan",
#         "type": "event",
#     },


#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "owner",
#                 "type": "address",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "spender",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256[]",
#                 "name": "indexes",
#                 "type": "uint256[]",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256[]",
#                 "name": "amounts",
#                 "type": "uint256[]",
#             },
#         ],
#         "name": "IncreaseLPAllowance",
#         "type": "event",
#     },


#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "borrower",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "debt",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "collateral",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "bond",
#                 "type": "uint256",
#             },
#         ],
#         "name": "Kick",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "claimableReservesRemaining",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "auctionPrice",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "currentBurnEpoch",
#                 "type": "uint256",
#             },
#         ],
#         "name": "KickReserveAuction",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "borrower",
#                 "type": "address",
#             }
#         ],
#         "name": "LoanStamped",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "lender",
#                 "type": "address",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "uint256",
#                 "name": "from",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "uint256",
#                 "name": "to",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "amount",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lpRedeemedFrom",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lpAwardedTo",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lup",
#                 "type": "uint256",
#             },
#         ],
#         "name": "MoveQuoteToken",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "claimer",
#                 "type": "address",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "uint256",
#                 "name": "index",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "amount",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lpRedeemed",
#                 "type": "uint256",
#             },
#         ],
#         "name": "RemoveCollateral",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "lender",
#                 "type": "address",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "uint256",
#                 "name": "index",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "amount",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lpRedeemed",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lup",
#                 "type": "uint256",
#             },
#         ],
#         "name": "RemoveQuoteToken",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "borrower",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "quoteRepaid",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "collateralPulled",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lup",
#                 "type": "uint256",
#             },
#         ],
#         "name": "RepayDebt",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "claimableReservesRemaining",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "auctionPrice",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "currentBurnEpoch",
#                 "type": "uint256",
#             },
#         ],
#         "name": "ReserveAuction",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "oldRate",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "newRate",
#                 "type": "uint256",
#             },
#         ],
#         "name": "ResetInterestRate",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "owner",
#                 "type": "address",
#             },
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "spender",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256[]",
#                 "name": "indexes",
#                 "type": "uint256[]",
#             },
#         ],
#         "name": "RevokeLPAllowance",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "lender",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "address[]",
#                 "name": "transferors",
#                 "type": "address[]",
#             },
#         ],
#         "name": "RevokeLPTransferors",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "borrower",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "settledDebt",
#                 "type": "uint256",
#             },
#         ],
#         "name": "Settle",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": true,
#                 "internalType": "address",
#                 "name": "borrower",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "amount",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "collateral",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "bondChange",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "bool",
#                 "name": "isReward",
#                 "type": "bool",
#             },
#         ],
#         "name": "Take",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": false,
#                 "internalType": "address",
#                 "name": "owner",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "address",
#                 "name": "newOwner",
#                 "type": "address",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256[]",
#                 "name": "indexes",
#                 "type": "uint256[]",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "lp",
#                 "type": "uint256",
#             },
#         ],
#         "name": "TransferLP",
#         "type": "event",
#     },
#     {
#         "anonymous": false,
#         "inputs": [
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "oldRate",
#                 "type": "uint256",
#             },
#             {
#                 "indexed": false,
#                 "internalType": "uint256",
#                 "name": "newRate",
#                 "type": "uint256",
#             },
#         ],
#         "name": "UpdateInterestRate",
#         "type": "event",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "amountToAdd_", "type": "uint256"},
#             {"internalType": "uint256", "name": "index_", "type": "uint256"},
#             {"internalType": "uint256", "name": "expiry_", "type": "uint256"},
#         ],
#         "name": "addCollateral",
#         "outputs": [
#             {"internalType": "uint256", "name": "bucketLP_", "type": "uint256"}
#         ],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "amount_", "type": "uint256"},
#             {"internalType": "uint256", "name": "index_", "type": "uint256"},
#             {"internalType": "uint256", "name": "expiry_", "type": "uint256"},
#             {"internalType": "bool", "name": "revertIfBelowLup_", "type": "bool"},
#         ],
#         "name": "addQuoteToken",
#         "outputs": [
#             {"internalType": "uint256", "name": "bucketLP_", "type": "uint256"}
#         ],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address[]", "name": "transferors_", "type": "address[]"}
#         ],
#         "name": "approveLPTransferors",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "", "type": "address"},
#             {"internalType": "address", "name": "", "type": "address"},
#         ],
#         "name": "approvedTransferors",
#         "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "address", "name": "borrower_", "type": "address"}],
#         "name": "auctionInfo",
#         "outputs": [
#             {"internalType": "address", "name": "kicker_", "type": "address"},
#             {"internalType": "uint256", "name": "bondFactor_", "type": "uint256"},
#             {"internalType": "uint256", "name": "bondSize_", "type": "uint256"},
#             {"internalType": "uint256", "name": "kickTime_", "type": "uint256"},
#             {"internalType": "uint256", "name": "kickMomp_", "type": "uint256"},
#             {"internalType": "uint256", "name": "neutralPrice_", "type": "uint256"},
#             {"internalType": "address", "name": "head_", "type": "address"},
#             {"internalType": "address", "name": "next_", "type": "address"},
#             {"internalType": "address", "name": "prev_", "type": "address"},
#             {"internalType": "bool", "name": "alreadyTaken_", "type": "bool"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "address", "name": "borrower_", "type": "address"}],
#         "name": "borrowerInfo",
#         "outputs": [
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "bucketIndex_", "type": "uint256"}
#         ],
#         "name": "bucketCollateralDust",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "pure",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "uint256", "name": "index_", "type": "uint256"}],
#         "name": "bucketExchangeRate",
#         "outputs": [
#             {"internalType": "uint256", "name": "exchangeRate_", "type": "uint256"}
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "uint256", "name": "index_", "type": "uint256"}],
#         "name": "bucketInfo",
#         "outputs": [
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "borrowerAddress_", "type": "address"},
#             {"internalType": "bool", "name": "depositTake_", "type": "bool"},
#             {"internalType": "uint256", "name": "index_", "type": "uint256"},
#         ],
#         "name": "bucketTake",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "burnEventEpoch_", "type": "uint256"}
#         ],
#         "name": "burnInfo",
#         "outputs": [
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "collateralAddress",
#         "outputs": [{"internalType": "address", "name": "", "type": "address"}],
#         "stateMutability": "pure",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "collateralScale",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "pure",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "currentBurnEpoch",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "debtInfo",
#         "outputs": [
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "spender_", "type": "address"},
#             {"internalType": "uint256[]", "name": "indexes_", "type": "uint256[]"},
#             {"internalType": "uint256[]", "name": "amounts_", "type": "uint256[]"},
#         ],
#         "name": "decreaseLPAllowance",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "uint256", "name": "debt_", "type": "uint256"}],
#         "name": "depositIndex",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "uint256", "name": "index_", "type": "uint256"}],
#         "name": "depositScale",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "depositSize",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "uint256", "name": "index_", "type": "uint256"}],
#         "name": "depositUpToIndex",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "depositUtilization",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "borrowerAddress_", "type": "address"},
#             {"internalType": "uint256", "name": "amountToBorrow_", "type": "uint256"},
#             {"internalType": "uint256", "name": "limitIndex_", "type": "uint256"},
#             {
#                 "internalType": "uint256",
#                 "name": "collateralToPledge_",
#                 "type": "uint256",
#             },
#         ],
#         "name": "drawDebt",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "emasInfo",
#         "outputs": [
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "token_", "type": "address"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "name": "flashFee",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {
#                 "internalType": "contract IERC3156FlashBorrower",
#                 "name": "receiver_",
#                 "type": "address",
#             },
#             {"internalType": "address", "name": "token_", "type": "address"},
#             {"internalType": "uint256", "name": "amount_", "type": "uint256"},
#             {"internalType": "bytes", "name": "data_", "type": "bytes"},
#         ],
#         "name": "flashLoan",
#         "outputs": [{"internalType": "bool", "name": "success_", "type": "bool"}],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "spender_", "type": "address"},
#             {"internalType": "uint256[]", "name": "indexes_", "type": "uint256[]"},
#             {"internalType": "uint256[]", "name": "amounts_", "type": "uint256[]"},
#         ],
#         "name": "increaseLPAllowance",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "inflatorInfo",
#         "outputs": [
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "uint256", "name": "rate_", "type": "uint256"}],
#         "name": "initialize",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "interestRateInfo",
#         "outputs": [
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "borrower_", "type": "address"},
#             {"internalType": "uint256", "name": "npLimitIndex_", "type": "uint256"},
#         ],
#         "name": "kick",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "kickReserveAuction",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "address", "name": "kicker_", "type": "address"}],
#         "name": "kickerInfo",
#         "outputs": [
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "index_", "type": "uint256"},
#             {"internalType": "address", "name": "lender_", "type": "address"},
#         ],
#         "name": "lenderInfo",
#         "outputs": [
#             {"internalType": "uint256", "name": "lpBalance_", "type": "uint256"},
#             {"internalType": "uint256", "name": "depositTime_", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "index_", "type": "uint256"},
#             {"internalType": "uint256", "name": "npLimitIndex_", "type": "uint256"},
#         ],
#         "name": "lenderKick",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "uint256", "name": "loanId_", "type": "uint256"}],
#         "name": "loanInfo",
#         "outputs": [
#             {"internalType": "address", "name": "", "type": "address"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "loansInfo",
#         "outputs": [
#             {"internalType": "address", "name": "", "type": "address"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "index_", "type": "uint256"},
#             {"internalType": "address", "name": "spender_", "type": "address"},
#             {"internalType": "address", "name": "owner_", "type": "address"},
#         ],
#         "name": "lpAllowance",
#         "outputs": [
#             {"internalType": "uint256", "name": "allowance_", "type": "uint256"}
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "address", "name": "token_", "type": "address"}],
#         "name": "maxFlashLoan",
#         "outputs": [{"internalType": "uint256", "name": "maxLoan_", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "maxAmount_", "type": "uint256"},
#             {"internalType": "uint256", "name": "fromIndex_", "type": "uint256"},
#             {"internalType": "uint256", "name": "toIndex_", "type": "uint256"},
#             {"internalType": "uint256", "name": "expiry_", "type": "uint256"},
#             {"internalType": "bool", "name": "revertIfBelowLup_", "type": "bool"},
#         ],
#         "name": "moveQuoteToken",
#         "outputs": [
#             {"internalType": "uint256", "name": "fromBucketLP_", "type": "uint256"},
#             {"internalType": "uint256", "name": "toBucketLP_", "type": "uint256"},
#             {"internalType": "uint256", "name": "movedAmount_", "type": "uint256"},
#         ],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [{"internalType": "bytes[]", "name": "data", "type": "bytes[]"}],
#         "name": "multicall",
#         "outputs": [{"internalType": "bytes[]", "name": "results", "type": "bytes[]"}],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "pledgedCollateral",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "poolType",
#         "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
#         "stateMutability": "pure",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "quoteTokenAddress",
#         "outputs": [{"internalType": "address", "name": "", "type": "address"}],
#         "stateMutability": "pure",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "quoteTokenScale",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "pure",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "maxAmount_", "type": "uint256"},
#             {"internalType": "uint256", "name": "index_", "type": "uint256"},
#         ],
#         "name": "removeCollateral",
#         "outputs": [
#             {"internalType": "uint256", "name": "removedAmount_", "type": "uint256"},
#             {"internalType": "uint256", "name": "redeemedLP_", "type": "uint256"},
#         ],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "maxAmount_", "type": "uint256"},
#             {"internalType": "uint256", "name": "index_", "type": "uint256"},
#         ],
#         "name": "removeQuoteToken",
#         "outputs": [
#             {"internalType": "uint256", "name": "removedAmount_", "type": "uint256"},
#             {"internalType": "uint256", "name": "redeemedLP_", "type": "uint256"},
#         ],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "borrowerAddress_", "type": "address"},
#             {
#                 "internalType": "uint256",
#                 "name": "maxQuoteTokenAmountToRepay_",
#                 "type": "uint256",
#             },
#             {
#                 "internalType": "uint256",
#                 "name": "collateralAmountToPull_",
#                 "type": "uint256",
#             },
#             {
#                 "internalType": "address",
#                 "name": "collateralReceiver_",
#                 "type": "address",
#             },
#             {"internalType": "uint256", "name": "limitIndex_", "type": "uint256"},
#         ],
#         "name": "repayDebt",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "reservesInfo",
#         "outputs": [
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#             {"internalType": "uint256", "name": "", "type": "uint256"},
#         ],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "spender_", "type": "address"},
#             {"internalType": "uint256[]", "name": "indexes_", "type": "uint256[]"},
#         ],
#         "name": "revokeLPAllowance",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address[]", "name": "transferors_", "type": "address[]"}
#         ],
#         "name": "revokeLPTransferors",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "borrowerAddress_", "type": "address"},
#             {"internalType": "uint256", "name": "maxDepth_", "type": "uint256"},
#         ],
#         "name": "settle",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "stampLoan",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "borrowerAddress_", "type": "address"},
#             {"internalType": "uint256", "name": "maxAmount_", "type": "uint256"},
#             {"internalType": "address", "name": "callee_", "type": "address"},
#             {"internalType": "bytes", "name": "data_", "type": "bytes"},
#         ],
#         "name": "take",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "uint256", "name": "maxAmount_", "type": "uint256"}
#         ],
#         "name": "takeReserves",
#         "outputs": [{"internalType": "uint256", "name": "amount_", "type": "uint256"}],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "totalAuctionsInPool",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "totalT0Debt",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "totalT0DebtInAuction",
#         "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
#         "stateMutability": "view",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "owner_", "type": "address"},
#             {"internalType": "address", "name": "newOwner_", "type": "address"},
#             {"internalType": "uint256[]", "name": "indexes_", "type": "uint256[]"},
#         ],
#         "name": "transferLP",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [],
#         "name": "updateInterest",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
#     {
#         "inputs": [
#             {"internalType": "address", "name": "recipient_", "type": "address"},
#             {"internalType": "uint256", "name": "maxAmount_", "type": "uint256"},
#         ],
#         "name": "withdrawBonds",
#         "outputs": [],
#         "stateMutability": "nonpayable",
#         "type": "function",
#     },
# ]
