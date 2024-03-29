# Generated by Django 4.2.3 on 2023-10-09 05:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0043_v2ethereumauction_v2ethereumauctionauctionsettle_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="v2ethereumauction",
            name="bond_factor",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v2ethereumauction",
            name="bond_size",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v2ethereumauction",
            name="last_take_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v2ethereumauction",
            name="neutral_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v2goerliauction",
            name="bond_factor",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v2goerliauction",
            name="bond_size",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v2goerliauction",
            name="last_take_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v2goerliauction",
            name="neutral_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
    ]
