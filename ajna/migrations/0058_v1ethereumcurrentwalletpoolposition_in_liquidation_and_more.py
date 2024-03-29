# Generated by Django 4.2.3 on 2023-10-20 11:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0057_v1ethereumpool_allowed_token_ids_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="v1ethereumcurrentwalletpoolposition",
            name="in_liquidation",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="v1ethereumwalletpoolposition",
            name="in_liquidation",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="v1goerlicurrentwalletpoolposition",
            name="in_liquidation",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="v1goerliwalletpoolposition",
            name="in_liquidation",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="v2ethereumcurrentwalletpoolposition",
            name="in_liquidation",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="v2ethereumwalletpoolposition",
            name="in_liquidation",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="v2goerlicurrentwalletpoolposition",
            name="in_liquidation",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="v2goerliwalletpoolposition",
            name="in_liquidation",
            field=models.BooleanField(default=False),
        ),
    ]
