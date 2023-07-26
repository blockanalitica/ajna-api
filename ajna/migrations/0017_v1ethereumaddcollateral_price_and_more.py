# Generated by Django 4.1.7 on 2023-06-21 08:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0016_v1goerliliquidationauction_collateral_token_address_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="v1ethereumaddcollateral",
            name="price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1ethereumaddquotetoken",
            name="price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1ethereumdrawdebt",
            name="collateral_token_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1ethereumdrawdebt",
            name="fee",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1ethereumdrawdebt",
            name="quote_token_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1ethereumremovecollateral",
            name="price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1ethereumremovequotetoken",
            name="price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1ethereumrepaydebt",
            name="collateral_token_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1ethereumrepaydebt",
            name="quote_token_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1goerliaddcollateral",
            name="price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1goerliaddquotetoken",
            name="price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1goerlidrawdebt",
            name="collateral_token_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1goerlidrawdebt",
            name="fee",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1goerlidrawdebt",
            name="quote_token_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1goerliremovecollateral",
            name="price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1goerliremovequotetoken",
            name="price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1goerlirepaydebt",
            name="collateral_token_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AddField(
            model_name="v1goerlirepaydebt",
            name="quote_token_price",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
    ]