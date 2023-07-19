import random

import factory
from faker.providers import BaseProvider


class EthereumProvider(BaseProvider):
    def ethereum_address(self):
        return "0x" + "".join(random.choices("0123456789abcdef", k=40))

    def transaction_hash(self):
        return "0x" + "".join(random.choices("0123456789abcdef", k=64))

    def cryptocurrency_code(self):
        return "".join(
            self.random_element("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(3)
        )


factory.Faker.add_provider(EthereumProvider)


class TokenFactory(factory.django.DjangoModelFactory):
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


class BucketFactory(factory.django.DjangoModelFactory):
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


class PoolFactory(factory.django.DjangoModelFactory):
    address = factory.Faker("ethereum_address")
    created_at_block_number = factory.Faker("random_number", digits=3)
    created_at_timestamp = factory.Faker("unix_time")
    collateral_token_address = factory.Faker("ethereum_address")
    quote_token_address = factory.Faker("ethereum_address")
    debt = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    inflator = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    borrow_rate = factory.Faker(
        "pydecimal", min_value=0, max_value=100, right_digits=18
    )
    lend_rate = factory.Faker("pydecimal", min_value=0, max_value=100, right_digits=18)
    deposit_fee_rate = factory.Faker(
        "pydecimal", min_value=0, max_value=100, right_digits=18
    )
    borrow_fee_rate = factory.Faker(
        "pydecimal", min_value=0, max_value=100, right_digits=18
    )
    pledged_collateral = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    total_interest_earned = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    tx_count = factory.Faker("random_number", digits=3)
    pool_size = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
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
    collateral_token_balance = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    quote_token_balance = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    datetime = factory.Faker("date_time_this_decade")


class AddCollateralFactory(factory.django.DjangoModelFactory):
    pool_address = factory.Faker("ethereum_address")
    bucket_index = factory.Sequence(lambda n: n)
    actor = factory.Faker("ethereum_address")
    index = factory.Sequence(lambda n: n)
    amount = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    lp_awarded = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    block_number = factory.Faker("random_number", digits=3)
    block_timestamp = factory.Faker("unix_time")
    transaction_hash = factory.Faker("transaction_hash")


class RemoveCollateralFactory(factory.django.DjangoModelFactory):
    pool_address = factory.Faker("ethereum_address")
    bucket_index = factory.Sequence(lambda n: n)
    claimer = factory.Faker("ethereum_address")
    index = factory.Sequence(lambda n: n)
    amount = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    lp_redeemed = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    block_number = factory.Faker("random_number", digits=3)
    block_timestamp = factory.Faker("unix_time")
    transaction_hash = factory.Faker("transaction_hash")


class AddQuoteTokenFactory(factory.django.DjangoModelFactory):
    pool_address = factory.Faker("ethereum_address")
    bucket_index = factory.Sequence(lambda n: n)
    lender = factory.Faker("ethereum_address")
    index = factory.Sequence(lambda n: n)
    amount = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    lp_awarded = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    lup = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    block_number = factory.Faker("random_number", digits=3)
    block_timestamp = factory.Faker("unix_time")
    transaction_hash = factory.Faker("transaction_hash")


class RemoveQuoteTokenFactory(factory.django.DjangoModelFactory):
    pool_address = factory.Faker("ethereum_address")
    bucket_index = factory.Sequence(lambda n: n)
    lender = factory.Faker("ethereum_address")
    index = factory.Sequence(lambda n: n)
    amount = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    lp_redeemed = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    lup = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    block_number = factory.Faker("random_number", digits=3)
    block_timestamp = factory.Faker("unix_time")
    transaction_hash = factory.Faker("transaction_hash")


class DrawDebtFactory(factory.django.DjangoModelFactory):
    pool_address = factory.Faker("ethereum_address")
    borrower = factory.Faker("ethereum_address")
    amount_borrowed = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    collateral_pledged = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    lup = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    block_number = factory.Faker("random_number", digits=3)
    block_timestamp = factory.Faker("unix_time")
    transaction_hash = factory.Faker("transaction_hash")


class RepayDebtFactory(factory.django.DjangoModelFactory):
    pool_address = factory.Faker("ethereum_address")
    borrower = factory.Faker("ethereum_address")
    quote_repaid = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    collateral_pulled = factory.Faker(
        "pydecimal", min_value=0, max_value=10000, right_digits=18
    )
    lup = factory.Faker("pydecimal", min_value=0, max_value=10000, right_digits=18)
    block_number = factory.Faker("random_number", digits=3)
    block_timestamp = factory.Faker("unix_time")
    transaction_hash = factory.Faker("transaction_hash")
