# Generated by Django 4.1.7 on 2023-04-21 19:06

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="V1EthereumPool",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fee_rate", models.DecimalField(decimal_places=18, max_digits=32)),
                ("current_debt", models.DecimalField(decimal_places=18, max_digits=32)),
                ("inflator", models.DecimalField(decimal_places=18, max_digits=32)),
                ("inflator_update", models.BigIntegerField()),
                (
                    "interest_rate",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "pledged_collateral",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "total_interest_earned",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("tx_count", models.BigIntegerField()),
                ("pool_size", models.DecimalField(decimal_places=18, max_digits=32)),
                ("loans_count", models.BigIntegerField()),
                ("max_borrower", models.CharField(max_length=42, null=True)),
                (
                    "pending_inflator",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "pending_interest_factor",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("hpb", models.DecimalField(decimal_places=18, max_digits=32)),
                ("hpb_index", models.IntegerField()),
                ("htp", models.DecimalField(decimal_places=18, max_digits=32)),
                ("htp_index", models.IntegerField()),
                ("lup", models.DecimalField(decimal_places=18, max_digits=32)),
                ("lup_index", models.IntegerField()),
                ("momp", models.DecimalField(decimal_places=18, max_digits=32)),
                ("reserves", models.DecimalField(decimal_places=18, max_digits=32)),
                (
                    "claimable_reserves",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "claimable_reserves_remaining",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "reserve_auction_price",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("reserve_auction_time_remaining", models.BigIntegerField()),
                ("burn_epoch", models.BigIntegerField()),
                (
                    "total_ajna_burned",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "min_debt_amount",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "collateralization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "actual_utilization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "target_utilization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "total_bond_escrowed",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("datetime", models.DateTimeField(db_index=True)),
                ("address", models.CharField(max_length=42, unique=True)),
                ("created_at_block_number", models.BigIntegerField()),
                ("created_at_timestamp", models.BigIntegerField()),
                (
                    "collateral_token_address",
                    models.CharField(db_index=True, max_length=42),
                ),
                ("quote_token_address", models.CharField(db_index=True, max_length=42)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="V1EthereumToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "underlying_address",
                    models.CharField(db_index=True, max_length=42, unique=True),
                ),
                ("symbol", models.CharField(db_index=True, max_length=64)),
                ("name", models.CharField(max_length=255)),
                ("decimals", models.BigIntegerField()),
                ("is_erc721", models.BooleanField()),
                (
                    "underlying_price",
                    models.DecimalField(decimal_places=18, max_digits=32, null=True),
                ),
                ("pool_count", models.BigIntegerField(null=True)),
                ("total_supply", models.BigIntegerField(null=True)),
                ("tx_count", models.BigIntegerField(null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="V1GoerliPool",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fee_rate", models.DecimalField(decimal_places=18, max_digits=32)),
                ("current_debt", models.DecimalField(decimal_places=18, max_digits=32)),
                ("inflator", models.DecimalField(decimal_places=18, max_digits=32)),
                ("inflator_update", models.BigIntegerField()),
                (
                    "interest_rate",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "pledged_collateral",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "total_interest_earned",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("tx_count", models.BigIntegerField()),
                ("pool_size", models.DecimalField(decimal_places=18, max_digits=32)),
                ("loans_count", models.BigIntegerField()),
                ("max_borrower", models.CharField(max_length=42, null=True)),
                (
                    "pending_inflator",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "pending_interest_factor",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("hpb", models.DecimalField(decimal_places=18, max_digits=32)),
                ("hpb_index", models.IntegerField()),
                ("htp", models.DecimalField(decimal_places=18, max_digits=32)),
                ("htp_index", models.IntegerField()),
                ("lup", models.DecimalField(decimal_places=18, max_digits=32)),
                ("lup_index", models.IntegerField()),
                ("momp", models.DecimalField(decimal_places=18, max_digits=32)),
                ("reserves", models.DecimalField(decimal_places=18, max_digits=32)),
                (
                    "claimable_reserves",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "claimable_reserves_remaining",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "reserve_auction_price",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("reserve_auction_time_remaining", models.BigIntegerField()),
                ("burn_epoch", models.BigIntegerField()),
                (
                    "total_ajna_burned",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "min_debt_amount",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "collateralization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "actual_utilization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "target_utilization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "total_bond_escrowed",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("datetime", models.DateTimeField(db_index=True)),
                ("address", models.CharField(max_length=42, unique=True)),
                ("created_at_block_number", models.BigIntegerField()),
                ("created_at_timestamp", models.BigIntegerField()),
                (
                    "collateral_token_address",
                    models.CharField(db_index=True, max_length=42),
                ),
                ("quote_token_address", models.CharField(db_index=True, max_length=42)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="V1GoerliToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "underlying_address",
                    models.CharField(db_index=True, max_length=42, unique=True),
                ),
                ("symbol", models.CharField(db_index=True, max_length=64)),
                ("name", models.CharField(max_length=255)),
                ("decimals", models.BigIntegerField()),
                ("is_erc721", models.BooleanField()),
                (
                    "underlying_price",
                    models.DecimalField(decimal_places=18, max_digits=32, null=True),
                ),
                ("pool_count", models.BigIntegerField(null=True)),
                ("total_supply", models.BigIntegerField(null=True)),
                ("tx_count", models.BigIntegerField(null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="V1GoerliPoolSnapshot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fee_rate", models.DecimalField(decimal_places=18, max_digits=32)),
                ("current_debt", models.DecimalField(decimal_places=18, max_digits=32)),
                ("inflator", models.DecimalField(decimal_places=18, max_digits=32)),
                ("inflator_update", models.BigIntegerField()),
                (
                    "interest_rate",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "pledged_collateral",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "total_interest_earned",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("tx_count", models.BigIntegerField()),
                ("pool_size", models.DecimalField(decimal_places=18, max_digits=32)),
                ("loans_count", models.BigIntegerField()),
                ("max_borrower", models.CharField(max_length=42, null=True)),
                (
                    "pending_inflator",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "pending_interest_factor",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("hpb", models.DecimalField(decimal_places=18, max_digits=32)),
                ("hpb_index", models.IntegerField()),
                ("htp", models.DecimalField(decimal_places=18, max_digits=32)),
                ("htp_index", models.IntegerField()),
                ("lup", models.DecimalField(decimal_places=18, max_digits=32)),
                ("lup_index", models.IntegerField()),
                ("momp", models.DecimalField(decimal_places=18, max_digits=32)),
                ("reserves", models.DecimalField(decimal_places=18, max_digits=32)),
                (
                    "claimable_reserves",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "claimable_reserves_remaining",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "reserve_auction_price",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("reserve_auction_time_remaining", models.BigIntegerField()),
                ("burn_epoch", models.BigIntegerField()),
                (
                    "total_ajna_burned",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "min_debt_amount",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "collateralization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "actual_utilization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "target_utilization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "total_bond_escrowed",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("datetime", models.DateTimeField(db_index=True)),
                (
                    "address",
                    models.CharField(db_index=True, max_length=42, unique=True),
                ),
            ],
            options={
                "abstract": False,
                "unique_together": {("address", "datetime")},
            },
        ),
        migrations.CreateModel(
            name="V1GoerliBucket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bucket_index", models.BigIntegerField()),
                (
                    "exchange_rate",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("pool_address", models.CharField(db_index=True, max_length=42)),
                ("collateral", models.DecimalField(decimal_places=18, max_digits=32)),
                ("deposit", models.DecimalField(decimal_places=18, max_digits=32)),
                ("lpb", models.DecimalField(decimal_places=18, max_digits=32)),
            ],
            options={
                "abstract": False,
                "unique_together": {("bucket_index", "pool_address")},
            },
        ),
        migrations.CreateModel(
            name="V1EthereumPoolSnapshot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fee_rate", models.DecimalField(decimal_places=18, max_digits=32)),
                ("current_debt", models.DecimalField(decimal_places=18, max_digits=32)),
                ("inflator", models.DecimalField(decimal_places=18, max_digits=32)),
                ("inflator_update", models.BigIntegerField()),
                (
                    "interest_rate",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "pledged_collateral",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "total_interest_earned",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("tx_count", models.BigIntegerField()),
                ("pool_size", models.DecimalField(decimal_places=18, max_digits=32)),
                ("loans_count", models.BigIntegerField()),
                ("max_borrower", models.CharField(max_length=42, null=True)),
                (
                    "pending_inflator",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "pending_interest_factor",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("hpb", models.DecimalField(decimal_places=18, max_digits=32)),
                ("hpb_index", models.IntegerField()),
                ("htp", models.DecimalField(decimal_places=18, max_digits=32)),
                ("htp_index", models.IntegerField()),
                ("lup", models.DecimalField(decimal_places=18, max_digits=32)),
                ("lup_index", models.IntegerField()),
                ("momp", models.DecimalField(decimal_places=18, max_digits=32)),
                ("reserves", models.DecimalField(decimal_places=18, max_digits=32)),
                (
                    "claimable_reserves",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "claimable_reserves_remaining",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "reserve_auction_price",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("reserve_auction_time_remaining", models.BigIntegerField()),
                ("burn_epoch", models.BigIntegerField()),
                (
                    "total_ajna_burned",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "min_debt_amount",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "collateralization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "actual_utilization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "target_utilization",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "total_bond_escrowed",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("datetime", models.DateTimeField(db_index=True)),
                (
                    "address",
                    models.CharField(db_index=True, max_length=42, unique=True),
                ),
            ],
            options={
                "abstract": False,
                "unique_together": {("address", "datetime")},
            },
        ),
        migrations.CreateModel(
            name="V1EthereumBucket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bucket_index", models.BigIntegerField()),
                (
                    "exchange_rate",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("pool_address", models.CharField(db_index=True, max_length=42)),
                ("collateral", models.DecimalField(decimal_places=18, max_digits=32)),
                ("deposit", models.DecimalField(decimal_places=18, max_digits=32)),
                ("lpb", models.DecimalField(decimal_places=18, max_digits=32)),
            ],
            options={
                "abstract": False,
                "unique_together": {("bucket_index", "pool_address")},
            },
        ),
    ]
