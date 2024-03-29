# Generated by Django 4.2.1 on 2023-07-05 08:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0021_alter_v1ethereumpool_collateralization_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="v1ethereumpool",
            name="collateralization",
        ),
        migrations.RemoveField(
            model_name="v1ethereumpool",
            name="reserve_auction_price",
        ),
        migrations.RemoveField(
            model_name="v1ethereumpool",
            name="reserve_auction_time_remaining",
        ),
        migrations.RemoveField(
            model_name="v1ethereumpoolsnapshot",
            name="reserve_auction_price",
        ),
        migrations.RemoveField(
            model_name="v1ethereumpoolsnapshot",
            name="reserve_auction_time_remaining",
        ),
        migrations.RemoveField(
            model_name="v1goerlipool",
            name="collateralization",
        ),
        migrations.RemoveField(
            model_name="v1goerlipool",
            name="reserve_auction_price",
        ),
        migrations.RemoveField(
            model_name="v1goerlipool",
            name="reserve_auction_time_remaining",
        ),
        migrations.RemoveField(
            model_name="v1goerlipoolsnapshot",
            name="reserve_auction_price",
        ),
        migrations.RemoveField(
            model_name="v1goerlipoolsnapshot",
            name="reserve_auction_time_remaining",
        ),
    ]
