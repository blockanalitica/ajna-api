# Generated by Django 4.2.3 on 2023-08-10 14:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0025_v1goerlimovequotetoken_v1ethereummovequotetoken"),
    ]

    operations = [
        migrations.CreateModel(
            name="V1EthereumGrantProposal",
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
                ("uid", models.CharField(db_index=True, max_length=100, unique=True)),
                ("description", models.JSONField()),
                ("executed", models.BooleanField()),
                (
                    "screening_votes_received",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "funding_votes_received",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "total_tokens_requested",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("start_block", models.BigIntegerField()),
                ("end_block", models.BigIntegerField(db_index=True)),
                ("funding_start_block_number", models.BigIntegerField()),
                ("finalize_start_block_number", models.BigIntegerField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="V1GoerliGrantProposal",
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
                ("uid", models.CharField(db_index=True, max_length=100, unique=True)),
                ("description", models.JSONField()),
                ("executed", models.BooleanField()),
                (
                    "screening_votes_received",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "funding_votes_received",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                (
                    "total_tokens_requested",
                    models.DecimalField(decimal_places=18, max_digits=32),
                ),
                ("start_block", models.BigIntegerField()),
                ("end_block", models.BigIntegerField(db_index=True)),
                ("funding_start_block_number", models.BigIntegerField()),
                ("finalize_start_block_number", models.BigIntegerField()),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
