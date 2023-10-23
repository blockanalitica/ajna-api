# Generated by Django 4.2.3 on 2023-10-16 10:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0055_v2ethereumauctionauctionsettle_collateral_token_price_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="v1ethereumpool",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="v1ethereumpoolsnapshot",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="v1ethereumtoken",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="v1goerlipool",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="v1goerlipoolsnapshot",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="v1goerlitoken",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="v2ethereumpool",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="v2ethereumpoolsnapshot",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="v2ethereumtoken",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="v2goerlipool",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="v2goerlipoolsnapshot",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="v2goerlitoken",
            name="erc",
            field=models.CharField(
                choices=[("erc20", "erc20"), ("erc721", "erc721")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="v1ethereumtoken",
            name="is_erc721",
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name="v1goerlitoken",
            name="is_erc721",
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name="v2ethereumtoken",
            name="is_erc721",
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name="v2goerlitoken",
            name="is_erc721",
            field=models.BooleanField(null=True),
        ),
    ]