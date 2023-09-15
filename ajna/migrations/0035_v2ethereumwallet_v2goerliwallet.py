# Generated by Django 4.2.3 on 2023-09-14 06:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0034_v1ethereumpoolevent_collateral_token_price_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="V2EthereumWallet",
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
                ("address", models.CharField(max_length=42, unique=True)),
                ("first_activity", models.DateTimeField(null=True)),
                ("last_activity", models.DateTimeField(null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="V2GoerliWallet",
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
                ("address", models.CharField(max_length=42, unique=True)),
                ("first_activity", models.DateTimeField(null=True)),
                ("last_activity", models.DateTimeField(null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
