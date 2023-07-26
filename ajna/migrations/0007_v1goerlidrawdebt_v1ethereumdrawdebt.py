# Generated by Django 4.1.7 on 2023-05-08 05:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0006_v1goerliremovequotetoken_v1ethereumremovequotetoken"),
    ]

    operations = [
        migrations.CreateModel(
            name="V1GoerliDrawDebt",
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
                ("pool_address", models.CharField(db_index=True, max_length=42)),
                ("borrower", models.CharField(max_length=42)),
                (
                    "amount_borrowed",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "collateral_pledged",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("lup", models.DecimalField(decimal_places=18, max_digits=32)),
                ("block_number", models.BigIntegerField()),
                ("block_timestamp", models.BigIntegerField()),
                ("transaction_hash", models.CharField(max_length=66)),
            ],
            options={
                "abstract": False,
                "unique_together": {("pool_address", "borrower", "transaction_hash")},
            },
        ),
        migrations.CreateModel(
            name="V1EthereumDrawDebt",
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
                ("pool_address", models.CharField(db_index=True, max_length=42)),
                ("borrower", models.CharField(max_length=42)),
                (
                    "amount_borrowed",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "collateral_pledged",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("lup", models.DecimalField(decimal_places=18, max_digits=32)),
                ("block_number", models.BigIntegerField()),
                ("block_timestamp", models.BigIntegerField()),
                ("transaction_hash", models.CharField(max_length=66)),
            ],
            options={
                "abstract": False,
                "unique_together": {("pool_address", "borrower", "transaction_hash")},
            },
        ),
    ]