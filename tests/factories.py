from datetime import datetime, timedelta
import random

import factory
from factory.django import DjangoModelFactory
from faker.providers import BaseProvider
from tests.utils import generate_ethereum_address, generate_transaction_hash


class EthereumProvider(BaseProvider):
    def ethereum_address(self):
        return generate_ethereum_address()

    def transaction_hash(self):
        return generate_transaction_hash()

    def subgraph_hash(self):
        return "0x{}".format("".join(random.choices("0123456789abcdef", k=72)))

    def cryptocurrency_code(self):
        return "".join(
            self.random_element("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
            for _ in range(random.randint(3, 6))
        )

    def block_number(self):
        return random.randrange(10000000, 20000000)

    def block_timestamp(self, block_number):
        # Calculate block timestamp by multiplying block nubmer with 14, which is
        # at the time of writing closest to average seconds per block, and adding that
        # number to the start of the eth
        dt = datetime(2015, 7, 30, 3, 26, 13)
        return int((dt + timedelta(seconds=block_number * 14)).timestamp())


factory.Faker.add_provider(EthereumProvider)


class PoolFactory(DjangoModelFactory):
    address = factory.Faker("ethereum_address")
    created_at_block_number = factory.Faker("block_number")
    created_at_timestamp = factory.Faker("unix_time")
    pool_size = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    debt = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    t0debt = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    inflator = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    pending_inflator = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    borrow_rate = factory.Faker(
        "pydecimal", min_value=0, max_value=100, right_digits=18
    )
    lend_rate = factory.Faker("pydecimal", min_value=0, max_value=100, right_digits=18)
    borrow_fee_rate = factory.Faker(
        "pydecimal", min_value=0, max_value=100, right_digits=18
    )
    deposit_fee_rate = factory.Faker(
        "pydecimal", min_value=0, max_value=100, right_digits=18
    )
    pledged_collateral = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    total_interest_earned = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    tx_count = factory.Faker("random_number", digits=3)

    loans_count = factory.Faker("random_number", digits=3)
    max_borrower = factory.Faker("ethereum_address")
    hpb = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    hpb_index = factory.Faker("random_number", digits=3)
    htp = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    htp_index = factory.Faker("random_number", digits=3)
    lup = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    lup_index = factory.Faker("random_number", digits=3)
    momp = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    reserves = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    claimable_reserves = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    claimable_reserves_remaining = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    burn_epoch = factory.Faker("random_number", digits=3)
    total_ajna_burned = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    min_debt_amount = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    utilization = factory.Faker("random_int", min=0, max=100)
    actual_utilization = factory.Faker("random_int", min=0, max=100)
    target_utilization = factory.Faker("random_int", min=0, max=100)
    total_bond_escrowed = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    datetime = factory.Faker("date_time_this_decade")
    quote_token_balance = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    collateral_token_balance = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    collateral_token_address = factory.Faker("ethereum_address")
    quote_token_address = factory.Faker("ethereum_address")


# TODO
class TokenFactory(DjangoModelFactory):
    underlying_address = factory.Faker("ethereum_address")
    symbol = factory.Faker("cryptocurrency_code")
    decimals = factory.Faker("random_int", min=0, max=18)
    is_erc721 = factory.Faker("boolean")
    underlying_price = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    pool_count = factory.Faker("random_number", digits=3)
    total_supply = factory.Faker("random_number", digits=3)
    tx_count = factory.Faker("random_number", digits=3)

    @factory.lazy_attribute
    def name(self):
        return f"{self.symbol} Token"


# TODO
class BucketFactory(DjangoModelFactory):
    bucket_index = factory.Sequence(lambda n: n)
    bucket_price = factory.Faker(
        "pydecimal", left_digits=3, right_digits=18, positive=True
    )
    exchange_rate = factory.Faker(
        "pydecimal", left_digits=3, right_digits=18, positive=True
    )
    pool_address = factory.Faker("ethereum_address")
    collateral = factory.Faker(
        "pydecimal", left_digits=3, right_digits=18, positive=True
    )
    deposit = factory.Faker("pydecimal", left_digits=3, right_digits=18, positive=True)
    lpb = factory.Faker("pydecimal", left_digits=3, right_digits=18, positive=True)


# TODO
class AddCollateralFactory(DjangoModelFactory):
    pool_address = factory.Faker("ethereum_address")
    bucket_index = factory.Sequence(lambda n: n)
    actor = factory.Faker("ethereum_address")
    index = factory.Sequence(lambda n: n)
    amount = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    lp_awarded = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    block_number = factory.Faker("block_number")
    block_timestamp = factory.Faker(
        "block_timestamp", block_number=factory.SelfAttribute("..block_number")
    )
    transaction_hash = factory.Faker("transaction_hash")


# TODO
class RemoveCollateralFactory(DjangoModelFactory):
    pool_address = factory.Faker("ethereum_address")
    bucket_index = factory.Sequence(lambda n: n)
    claimer = factory.Faker("ethereum_address")
    index = factory.Sequence(lambda n: n)
    amount = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    lp_redeemed = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    block_number = factory.Faker("block_number")
    block_timestamp = factory.Faker(
        "block_timestamp", block_number=factory.SelfAttribute("..block_number")
    )
    transaction_hash = factory.Faker("transaction_hash")


class AddQuoteTokenFactory(DjangoModelFactory):
    pool_address = factory.Faker("ethereum_address")
    bucket_index = factory.Sequence(lambda n: n)
    bucket_price = factory.Faker(
        "pydecimal", min_value=0, max_value=1000, right_digits=18
    )
    lender = factory.Faker("ethereum_address")
    index = factory.Sequence(lambda n: n)
    amount = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    lp_awarded = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    lup = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    block_number = factory.Faker("block_number")
    block_timestamp = factory.Faker(
        "block_timestamp", block_number=factory.SelfAttribute("..block_number")
    )
    transaction_hash = factory.Faker("transaction_hash")
    price = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    deposit_fee_rate = factory.Faker(
        "pydecimal", min_value=0, max_value=100, right_digits=18
    )
    fee = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)


class RemoveQuoteTokenFactory(DjangoModelFactory):
    pool_address = factory.Faker("ethereum_address")
    bucket_index = factory.Sequence(lambda n: n)
    lender = factory.Faker("ethereum_address")
    index = factory.Sequence(lambda n: n)
    amount = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    lp_redeemed = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    lup = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    block_number = factory.Faker("block_number")
    block_timestamp = factory.Faker(
        "block_timestamp", block_number=factory.SelfAttribute("..block_number")
    )
    transaction_hash = factory.Faker("transaction_hash")
    price = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)


class MoveQuoteTokenFactory(DjangoModelFactory):
    pool_address = factory.Faker("ethereum_address")
    bucket_index_from = factory.Sequence(lambda n: n)
    bucket_index_to = factory.Sequence(lambda n: n)
    lender = factory.Faker("ethereum_address")
    amount = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    lp_redeemed_from = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    lp_awarded_to = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    lup = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    block_number = factory.Faker("block_number")
    block_timestamp = factory.Faker(
        "block_timestamp", block_number=factory.SelfAttribute("..block_number")
    )
    transaction_hash = factory.Faker("transaction_hash")
    price = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)


class DrawDebtFactory(DjangoModelFactory):
    index = factory.Faker("subgraph_hash")
    pool_address = factory.Faker("ethereum_address")
    borrower = factory.Faker("ethereum_address")
    amount_borrowed = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    collateral_pledged = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    lup = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    block_number = factory.Faker("block_number")
    block_timestamp = factory.Faker(
        "block_timestamp", block_number=factory.SelfAttribute("..block_number")
    )
    transaction_hash = factory.Faker("transaction_hash")
    fee = factory.Faker("pydecimal", min_value=0, max_value=100, right_digits=18)
    borrow_fee_rate = factory.Faker(
        "pydecimal", min_value=0, max_value=100, right_digits=18
    )
    collateral_token_price = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    quote_token_price = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )


class RepayDebtFactory(DjangoModelFactory):
    index = factory.Faker("subgraph_hash")
    pool_address = factory.Faker("ethereum_address")
    borrower = factory.Faker("ethereum_address")
    quote_repaid = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    collateral_pulled = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    lup = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    block_number = factory.Faker("block_number")
    block_timestamp = factory.Faker(
        "block_timestamp", block_number=factory.SelfAttribute("..block_number")
    )
    transaction_hash = factory.Faker("transaction_hash")
    collateral_token_price = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    quote_token_price = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
