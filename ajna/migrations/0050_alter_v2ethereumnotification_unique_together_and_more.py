# Generated by Django 4.2.3 on 2023-10-13 13:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0049_v1ethereumwalletpoolposition_lup_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="v2ethereumnotification",
            unique_together={("pool_address", "key", "type")},
        ),
        migrations.AlterUniqueTogether(
            name="v2goerlinotification",
            unique_together={("pool_address", "key", "type")},
        ),
    ]
