from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


class PoolBase(models.Model):
    pool_size = models.DecimalField(max_digits=32, decimal_places=18)
    debt = models.DecimalField(max_digits=32, decimal_places=18)
    t0debt = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    inflator = models.DecimalField(max_digits=32, decimal_places=18)
    pending_inflator = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    borrow_rate = models.DecimalField(max_digits=32, decimal_places=18)
    lend_rate = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    borrow_fee_rate = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    deposit_fee_rate = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    pledged_collateral = models.DecimalField(max_digits=32, decimal_places=18)
    total_interest_earned = models.DecimalField(max_digits=32, decimal_places=18)
    tx_count = models.BigIntegerField(null=True)
    loans_count = models.BigIntegerField()
    max_borrower = models.CharField(max_length=42, null=True)
    hpb = models.DecimalField(max_digits=32, decimal_places=18)
    hpb_index = models.IntegerField()
    htp = models.DecimalField(max_digits=32, decimal_places=18)
    htp_index = models.IntegerField()
    lup = models.DecimalField(max_digits=32, decimal_places=18)
    lup_index = models.IntegerField()
    momp = models.DecimalField(max_digits=32, decimal_places=18)
    reserves = models.DecimalField(max_digits=32, decimal_places=18)
    claimable_reserves = models.DecimalField(max_digits=32, decimal_places=18)
    claimable_reserves_remaining = models.DecimalField(max_digits=32, decimal_places=18)
    burn_epoch = models.BigIntegerField()
    total_ajna_burned = models.DecimalField(max_digits=32, decimal_places=18)
    min_debt_amount = models.DecimalField(max_digits=32, decimal_places=18)
    # Our calculation of utilization
    utilization = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    current_meaningful_utilization = models.DecimalField(
        max_digits=32, decimal_places=18, null=True
    )
    actual_utilization = models.DecimalField(max_digits=32, decimal_places=18)  # MAU
    target_utilization = models.DecimalField(max_digits=32, decimal_places=18)  # TU
    total_bond_escrowed = models.DecimalField(
        max_digits=32, decimal_places=18, null=True
    )

    datetime = models.DateTimeField(db_index=True)

    quote_token_balance = models.DecimalField(
        max_digits=32, decimal_places=18, null=True
    )
    collateral_token_balance = models.DecimalField(
        max_digits=32, decimal_places=18, null=True
    )
    collateral_token_address = models.CharField(max_length=42, db_index=True, null=True)
    quote_token_address = models.CharField(max_length=42, db_index=True, null=True)
    volume_today = models.DecimalField(max_digits=32, decimal_places=18, null=True)

    class Meta:
        abstract = True


class Pool(PoolBase):
    address = models.CharField(max_length=42, unique=True)
    created_at_block_number = models.BigIntegerField()
    created_at_timestamp = models.BigIntegerField()

    def __str__(self):
        return self.address

    class Meta:
        abstract = True


class PoolSnapshot(PoolBase):
    address = models.CharField(max_length=42, db_index=True)
    collateral_token_price = models.DecimalField(
        max_digits=32, decimal_places=18, null=True
    )
    quote_token_price = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    collateralization = models.DecimalField(max_digits=32, decimal_places=18, null=True)

    def __str__(self):
        return self.address

    class Meta:
        abstract = True
        unique_together = ("address", "datetime")


class Token(models.Model):
    underlying_address = models.CharField(max_length=42, unique=True, db_index=True)
    symbol = models.CharField(max_length=64, db_index=True)
    name = models.CharField(max_length=255)
    decimals = models.BigIntegerField()
    is_erc721 = models.BooleanField()
    underlying_price = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    pool_count = models.BigIntegerField(null=True)
    total_supply = models.BigIntegerField(null=True)
    tx_count = models.BigIntegerField(null=True)

    def __str__(self):
        return self.symbol

    class Meta:
        abstract = True


class Bucket(models.Model):
    bucket_index = models.BigIntegerField()
    bucket_price = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    exchange_rate = models.DecimalField(max_digits=32, decimal_places=18)
    pool_address = models.CharField(max_length=42, db_index=True)
    collateral = models.DecimalField(max_digits=32, decimal_places=18)
    deposit = models.DecimalField(max_digits=32, decimal_places=18)
    lpb = models.DecimalField(max_digits=32, decimal_places=18)

    class Meta:
        abstract = True
        unique_together = ("bucket_index", "pool_address")


##########
# Events #
##########


class AddCollateral(models.Model):
    pool_address = models.CharField(max_length=42, db_index=True)
    bucket_index = models.BigIntegerField()
    actor = models.CharField(max_length=42)
    index = models.BigIntegerField()
    amount = models.DecimalField(max_digits=32, decimal_places=18)
    lp_awarded = models.DecimalField(max_digits=32, decimal_places=18)
    block_number = models.BigIntegerField()
    block_timestamp = models.BigIntegerField()
    transaction_hash = models.CharField(max_length=66)
    price = models.DecimalField(max_digits=32, decimal_places=18, null=True)

    class Meta:
        abstract = True
        unique_together = (
            "pool_address",
            "bucket_index",
            "actor",
            "index",
            "transaction_hash",
        )


class RemoveCollateral(models.Model):
    pool_address = models.CharField(max_length=42, db_index=True)
    bucket_index = models.BigIntegerField()
    claimer = models.CharField(max_length=42)
    index = models.BigIntegerField()
    amount = models.DecimalField(max_digits=32, decimal_places=18)
    lp_redeemed = models.DecimalField(max_digits=32, decimal_places=18)
    block_number = models.BigIntegerField()
    block_timestamp = models.BigIntegerField()
    transaction_hash = models.CharField(max_length=66)
    price = models.DecimalField(max_digits=32, decimal_places=18, null=True)

    class Meta:
        abstract = True
        unique_together = (
            "pool_address",
            "bucket_index",
            "claimer",
            "transaction_hash",
        )


class AddQuoteToken(models.Model):
    pool_address = models.CharField(max_length=42, db_index=True)
    bucket_index = models.BigIntegerField()
    bucket_price = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    lender = models.CharField(max_length=42)
    index = models.BigIntegerField()
    amount = models.DecimalField(max_digits=32, decimal_places=18)
    lp_awarded = models.DecimalField(max_digits=32, decimal_places=18)
    lup = models.DecimalField(max_digits=32, decimal_places=18)
    block_number = models.BigIntegerField()
    block_timestamp = models.BigIntegerField()
    transaction_hash = models.CharField(max_length=66)
    price = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    deposit_fee_rate = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    fee = models.DecimalField(max_digits=32, decimal_places=18, null=True)

    class Meta:
        abstract = True
        unique_together = (
            "pool_address",
            "bucket_index",
            "lender",
            "index",
            "transaction_hash",
        )


class RemoveQuoteToken(models.Model):
    pool_address = models.CharField(max_length=42, db_index=True)
    bucket_index = models.BigIntegerField()
    lender = models.CharField(max_length=42)
    index = models.BigIntegerField()
    amount = models.DecimalField(max_digits=32, decimal_places=18)
    lp_redeemed = models.DecimalField(max_digits=32, decimal_places=18)
    lup = models.DecimalField(max_digits=32, decimal_places=18)
    block_number = models.BigIntegerField()
    block_timestamp = models.BigIntegerField()
    transaction_hash = models.CharField(max_length=66)
    price = models.DecimalField(max_digits=32, decimal_places=18, null=True)

    class Meta:
        abstract = True
        unique_together = ("pool_address", "bucket_index", "lender", "transaction_hash")


class MoveQuoteToken(models.Model):
    pool_address = models.CharField(max_length=42, db_index=True)
    bucket_index_from = models.BigIntegerField()
    bucket_index_to = models.BigIntegerField()
    lender = models.CharField(max_length=42)
    amount = models.DecimalField(max_digits=32, decimal_places=18)
    lp_redeemed_from = models.DecimalField(max_digits=32, decimal_places=18)
    lp_awarded_to = models.DecimalField(max_digits=32, decimal_places=18)
    lup = models.DecimalField(max_digits=32, decimal_places=18)
    block_number = models.BigIntegerField()
    block_timestamp = models.BigIntegerField()
    transaction_hash = models.CharField(max_length=66)
    price = models.DecimalField(max_digits=32, decimal_places=18, null=True)

    class Meta:
        abstract = True
        unique_together = (
            "pool_address",
            "bucket_index_from",
            "bucket_index_to",
            "lender",
            "transaction_hash",
        )


class DrawDebt(models.Model):
    index = models.CharField(max_length=128, null=True)
    pool_address = models.CharField(max_length=42, db_index=True)
    borrower = models.CharField(max_length=42)
    amount_borrowed = models.DecimalField(max_digits=32, decimal_places=18)
    collateral_pledged = models.DecimalField(max_digits=32, decimal_places=18)
    lup = models.DecimalField(max_digits=32, decimal_places=18)
    block_number = models.BigIntegerField()
    block_timestamp = models.BigIntegerField()
    transaction_hash = models.CharField(max_length=66)
    fee = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    borrow_fee_rate = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    collateral_token_price = models.DecimalField(
        max_digits=32, decimal_places=18, null=True
    )
    quote_token_price = models.DecimalField(max_digits=32, decimal_places=18, null=True)

    class Meta:
        abstract = True
        unique_together = ("index", "pool_address", "borrower", "transaction_hash")


class RepayDebt(models.Model):
    index = models.CharField(max_length=128, null=True)
    pool_address = models.CharField(max_length=42, db_index=True)
    borrower = models.CharField(max_length=42)
    quote_repaid = models.DecimalField(max_digits=32, decimal_places=18)
    collateral_pulled = models.DecimalField(max_digits=32, decimal_places=18)
    lup = models.DecimalField(max_digits=32, decimal_places=18)
    block_number = models.BigIntegerField()
    block_timestamp = models.BigIntegerField()
    transaction_hash = models.CharField(max_length=66)
    collateral_token_price = models.DecimalField(
        max_digits=32, decimal_places=18, null=True
    )
    quote_token_price = models.DecimalField(max_digits=32, decimal_places=18, null=True)

    class Meta:
        abstract = True
        unique_together = ("index", "pool_address", "borrower", "transaction_hash")


class PriceFeed(models.Model):
    price = models.DecimalField(max_digits=32, decimal_places=18)
    timestamp = models.BigIntegerField(db_index=True)
    datetime = models.DateTimeField(null=True)
    underlying_address = models.CharField(max_length=42, db_index=True)

    def __str__(self):
        return self.underlying_address

    def __repr__(self):
        return f"<{self.__class__.__name__}: underlying_address={self.underlying_address} price={self.price}>"

    class Meta:
        abstract = True
        get_latest_by = "datetime"
        ordering = ("-datetime",)
        indexes = [
            models.Index(fields=["underlying_address"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["datetime"]),
            models.Index(fields=["underlying_address", "datetime"]),
        ]


class LiquidationAuction(models.Model):
    uid = models.CharField(max_length=256, null=True)
    pool_address = models.CharField(max_length=42, db_index=True)
    settled = models.BooleanField()
    settle_time = models.BigIntegerField(null=True)
    datetime = models.DateTimeField()
    neutral_price = models.DecimalField(max_digits=32, decimal_places=18)
    kicker = models.CharField(max_length=42)
    kick_time = models.BigIntegerField()
    debt = models.DecimalField(max_digits=32, decimal_places=18)
    collateral_remaining = models.DecimalField(max_digits=32, decimal_places=18)
    collateral = models.DecimalField(max_digits=32, decimal_places=18)
    borrower = models.CharField(max_length=42)
    wallet_address = models.CharField(max_length=42, null=True)
    bond_size = models.DecimalField(max_digits=32, decimal_places=18)
    bond_factor = models.DecimalField(max_digits=32, decimal_places=18)
    last_take_price = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    debt_remaining = models.DecimalField(max_digits=32, decimal_places=18)

    collateral_underlying_price = models.DecimalField(
        max_digits=32, decimal_places=18, null=True
    )
    debt_underlying_price = models.DecimalField(
        max_digits=32, decimal_places=18, null=True
    )

    collateral_token_address = models.CharField(max_length=42, null=True)
    debt_token_address = models.CharField(max_length=42, null=True)

    class Meta:
        get_latest_by = "datetime"
        ordering = ("-datetime",)
        abstract = True


class PoolVolumeSnapshot(models.Model):
    pool_address = models.CharField(max_length=42, db_index=True)
    amount = models.DecimalField(max_digits=32, decimal_places=18)
    date = models.DateField()

    class Meta:
        abstract = True
        unique_together = ("pool_address", "date")


class GrantProposal(models.Model):
    uid = models.CharField(max_length=100, db_index=True, unique=True)
    description = models.JSONField()
    executed = models.BooleanField()
    screening_votes_received = models.DecimalField(max_digits=32, decimal_places=18)
    funding_votes_received = models.DecimalField(max_digits=32, decimal_places=18)
    total_tokens_requested = models.DecimalField(max_digits=32, decimal_places=18)
    start_block = models.BigIntegerField()
    end_block = models.BigIntegerField(db_index=True)
    funding_start_block_number = models.BigIntegerField()
    finalize_start_block_number = models.BigIntegerField()

    class Meta:
        abstract = True


class PoolEvent(models.Model):
    pool_address = models.CharField(max_length=42)
    wallet_addresses = ArrayField(models.CharField(max_length=42), null=True)
    bucket_indexes = ArrayField(models.IntegerField(), null=True)
    block_number = models.BigIntegerField()
    block_datetime = models.DateTimeField()
    order_index = models.CharField(max_length=26)
    transaction_hash = models.CharField(max_length=66)
    name = models.CharField(max_length=42)
    data = models.JSONField()
    collateral_token_price = models.DecimalField(
        max_digits=32, decimal_places=18, null=True
    )
    quote_token_price = models.DecimalField(max_digits=32, decimal_places=18, null=True)

    class Meta:
        abstract = True
        unique_together = ("pool_address", "order_index")
        indexes = [
            models.Index(fields=["pool_address", "order_index"]),
            models.Index(fields=["pool_address", "wallet_addresses", "order_index"]),
            models.Index(fields=["pool_address", "wallet_addresses"]),
            models.Index(fields=["pool_address"]),
            models.Index(fields=["order_index"]),
        ]


class CurrentWalletPoolPosition(models.Model):
    wallet_address = models.CharField(max_length=42, db_index=True)
    pool_address = models.CharField(max_length=42, db_index=True)

    supply = models.DecimalField(max_digits=32, decimal_places=18)
    collateral = models.DecimalField(max_digits=32, decimal_places=18)
    t0debt = models.DecimalField(max_digits=32, decimal_places=18)
    debt = models.DecimalField(max_digits=32, decimal_places=18)

    datetime = models.DateTimeField()
    block_number = models.BigIntegerField(db_index=True)

    class Meta:
        unique_together = [
            "wallet_address",
            "block_number",
            "pool_address",
        ]
        get_latest_by = "block_number"
        ordering = ("block_number",)
        abstract = True


class WalletPoolPosition(models.Model):
    wallet_address = models.CharField(max_length=42, db_index=True)
    pool_address = models.CharField(max_length=42, db_index=True)

    supply = models.DecimalField(max_digits=32, decimal_places=18)
    collateral = models.DecimalField(max_digits=32, decimal_places=18)
    t0debt = models.DecimalField(max_digits=32, decimal_places=18)
    debt = models.DecimalField(max_digits=32, decimal_places=18)

    datetime = models.DateTimeField()
    block_number = models.BigIntegerField(db_index=True)

    class Meta:
        unique_together = [
            "wallet_address",
            "block_number",
            "pool_address",
        ]
        get_latest_by = "block_number"
        ordering = ("block_number",)
        abstract = True


class PoolBucketState(models.Model):
    pool_address = models.CharField(max_length=42)
    bucket_index = models.IntegerField()
    collateral = models.DecimalField(max_digits=32, decimal_places=18)
    deposit = models.DecimalField(max_digits=32, decimal_places=18)
    bucket_price = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    exchange_rate = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    lpb = models.DecimalField(max_digits=32, decimal_places=18, null=True)
    block_number = models.BigIntegerField()
    block_datetime = models.DateTimeField()

    class Meta:
        abstract = True
        unique_together = ("pool_address", "bucket_index", "block_number")
        indexes = [
            models.Index(fields=["pool_address", "bucket_index", "block_number"]),
            models.Index(fields=["pool_address", "bucket_index"]),
            models.Index(fields=["pool_address"]),
            models.Index(fields=["bucket_index"]),
            models.Index(fields=["block_number"]),
            models.Index(fields=["block_datetime"]),
        ]


class WalletPoolBucketState(models.Model):
    wallet_address = models.CharField(max_length=42)
    pool_address = models.CharField(max_length=42)
    bucket_index = models.IntegerField()
    deposit = models.DecimalField(max_digits=32, decimal_places=18)
    block_number = models.BigIntegerField()
    block_datetime = models.DateTimeField()

    class Meta:
        abstract = True
        unique_together = (
            "pool_address",
            "wallet_address",
            "bucket_index",
            "block_number",
        )
        indexes = [
            models.Index(
                fields=[
                    "pool_address",
                    "wallet_address",
                    "bucket_index",
                    "block_number",
                ]
            ),
            models.Index(fields=["pool_address", "wallet_address", "bucket_index"]),
            models.Index(fields=["pool_address"]),
            models.Index(fields=["wallet_address"]),
            models.Index(fields=["bucket_index"]),
            models.Index(fields=["block_number"]),
            models.Index(fields=["block_datetime"]),
        ]


class Wallet(models.Model):
    address = models.CharField(max_length=42, unique=True)
    first_activity = models.DateTimeField(null=True)
    last_activity = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class Notification(models.Model):
    type = models.TextField()
    key = models.TextField()
    data = models.JSONField(encoder=DjangoJSONEncoder)
    activity = models.JSONField(null=True, encoder=DjangoJSONEncoder)
    datetime = models.DateTimeField(db_index=True)
    pool_address = models.CharField(max_length=42, null=True)

    class Meta:
        abstract = True
        get_latest_by = "datetime"
        ordering = ("-datetime",)
        unique_together = ("pool_address", "key")
