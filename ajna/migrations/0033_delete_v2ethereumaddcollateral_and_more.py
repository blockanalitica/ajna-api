# Generated by Django 4.2.3 on 2023-09-12 07:11

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0032_v1ethereumpoolbucketstate_bucket_price_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="V2EthereumAddCollateral",
        ),
        migrations.DeleteModel(
            name="V2EthereumAddQuoteToken",
        ),
        migrations.DeleteModel(
            name="V2EthereumDrawDebt",
        ),
        migrations.DeleteModel(
            name="V2EthereumMoveQuoteToken",
        ),
        migrations.DeleteModel(
            name="V2EthereumRemoveCollateral",
        ),
        migrations.DeleteModel(
            name="V2EthereumRemoveQuoteToken",
        ),
        migrations.DeleteModel(
            name="V2EthereumRepayDebt",
        ),
        migrations.DeleteModel(
            name="V2GoerliAddCollateral",
        ),
        migrations.DeleteModel(
            name="V2GoerliAddQuoteToken",
        ),
        migrations.DeleteModel(
            name="V2GoerliDrawDebt",
        ),
        migrations.DeleteModel(
            name="V2GoerliMoveQuoteToken",
        ),
        migrations.DeleteModel(
            name="V2GoerliRemoveCollateral",
        ),
        migrations.DeleteModel(
            name="V2GoerliRemoveQuoteToken",
        ),
        migrations.DeleteModel(
            name="V2GoerliRepayDebt",
        ),
    ]
