# Generated by Django 4.2.3 on 2023-09-22 13:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0036_v2ethereumnotification_v2goerlinotification"),
    ]

    operations = [
        migrations.AddField(
            model_name="v1ethereumpool",
            name="volume_today",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1ethereumpoolsnapshot",
            name="volume_today",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1goerlipool",
            name="volume_today",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1goerlipoolsnapshot",
            name="volume_today",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v2ethereumpool",
            name="volume_today",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v2ethereumpoolsnapshot",
            name="volume_today",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v2goerlipool",
            name="volume_today",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v2goerlipoolsnapshot",
            name="volume_today",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
    ]
