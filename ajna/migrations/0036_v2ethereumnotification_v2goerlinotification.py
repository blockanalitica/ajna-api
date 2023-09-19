# Generated by Django 4.2.3 on 2023-09-19 07:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0035_v2ethereumwallet_v2goerliwallet"),
    ]

    operations = [
        migrations.CreateModel(
            name="V2EthereumNotification",
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
                ("type", models.TextField()),
                ("key", models.TextField(unique=True)),
                ("data", models.JSONField()),
                ("activity", models.JSONField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="V2GoerliNotification",
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
                ("type", models.TextField()),
                ("key", models.TextField(unique=True)),
                ("data", models.JSONField()),
                ("activity", models.JSONField()),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
