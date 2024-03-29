# Generated by Django 4.2.3 on 2023-10-14 12:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0050_alter_v2ethereumnotification_unique_together_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="v2ethereumauction",
            name="borrower_eoa",
            field=models.CharField(max_length=42, null=True),
        ),
        migrations.AddField(
            model_name="v2ethereumauction",
            name="kicker_eoa",
            field=models.CharField(max_length=42, null=True),
        ),
        migrations.AddField(
            model_name="v2goerliauction",
            name="borrower_eoa",
            field=models.CharField(max_length=42, null=True),
        ),
        migrations.AddField(
            model_name="v2goerliauction",
            name="kicker_eoa",
            field=models.CharField(max_length=42, null=True),
        ),
    ]
