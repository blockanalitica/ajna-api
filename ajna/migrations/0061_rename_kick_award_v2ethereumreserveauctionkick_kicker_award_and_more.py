# Generated by Django 4.2.3 on 2023-10-27 09:58

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0060_v2ethereumreserveauction_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="v2ethereumreserveauctionkick",
            old_name="kick_award",
            new_name="kicker_award",
        ),
        migrations.RenameField(
            model_name="v2goerlireserveauctionkick",
            old_name="kick_award",
            new_name="kicker_award",
        ),
    ]
