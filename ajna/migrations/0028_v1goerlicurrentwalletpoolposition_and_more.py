# Generated by Django 4.2.3 on 2023-08-21 07:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0027_v1ethereumpool_current_meaningful_utilization_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="V1GoerliCurrentWalletPoolPosition",
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
                ("wallet_address", models.CharField(db_index=True, max_length=42)),
                ("pool_address", models.CharField(db_index=True, max_length=42)),
                ("supply", models.DecimalField(decimal_places=18, max_digits=32)),
                ("collateral", models.DecimalField(decimal_places=18, max_digits=32)),
                ("t0debt", models.DecimalField(decimal_places=18, max_digits=32)),
                ("debt", models.DecimalField(decimal_places=18, max_digits=32)),
                ("datetime", models.DateTimeField()),
                ("block_number", models.BigIntegerField(db_index=True)),
            ],
            options={
                "ordering": ("block_number",),
                "get_latest_by": "block_number",
                "abstract": False,
                "unique_together": {("wallet_address", "block_number", "pool_address")},
            },
        ),
        migrations.CreateModel(
            name="V1EthereumCurrentWalletPoolPosition",
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
                ("wallet_address", models.CharField(db_index=True, max_length=42)),
                ("pool_address", models.CharField(db_index=True, max_length=42)),
                ("supply", models.DecimalField(decimal_places=18, max_digits=32)),
                ("collateral", models.DecimalField(decimal_places=18, max_digits=32)),
                ("t0debt", models.DecimalField(decimal_places=18, max_digits=32)),
                ("debt", models.DecimalField(decimal_places=18, max_digits=32)),
                ("datetime", models.DateTimeField()),
                ("block_number", models.BigIntegerField(db_index=True)),
            ],
            options={
                "ordering": ("block_number",),
                "get_latest_by": "block_number",
                "abstract": False,
                "unique_together": {("wallet_address", "block_number", "pool_address")},
            },
        ),
    ]