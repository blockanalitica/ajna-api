# Generated by Django 4.2.3 on 2024-01-10 06:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0077_alter_v1ethereumpool_debt_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="v1ethereumcurrentwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v1ethereumliquidationauction",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v1ethereumwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v1ethereumwalletpoolposition",
            name="pending_inflator",
            field=models.DecimalField(decimal_places=18, max_digits=40, null=True),
        ),
        migrations.AlterField(
            model_name="v1goerlicurrentwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v1goerliliquidationauction",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v1goerliwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v1goerliwalletpoolposition",
            name="pending_inflator",
            field=models.DecimalField(decimal_places=18, max_digits=40, null=True),
        ),
        migrations.AlterField(
            model_name="v2ethereumcurrentwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v2ethereumreserveauctionkick",
            name="kicker_award",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v2ethereumwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v2ethereumwalletpoolposition",
            name="pending_inflator",
            field=models.DecimalField(decimal_places=18, max_digits=40, null=True),
        ),
        migrations.AlterField(
            model_name="v2goerlicurrentwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v2goerlireserveauctionkick",
            name="kicker_award",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v2goerliwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v2goerliwalletpoolposition",
            name="pending_inflator",
            field=models.DecimalField(decimal_places=18, max_digits=40, null=True),
        ),
        migrations.AlterField(
            model_name="v3arbitrumcurrentwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3arbitrumreserveauctionkick",
            name="kicker_award",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v3arbitrumwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3arbitrumwalletpoolposition",
            name="pending_inflator",
            field=models.DecimalField(decimal_places=18, max_digits=40, null=True),
        ),
        migrations.AlterField(
            model_name="v3basecurrentwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3basereserveauctionkick",
            name="kicker_award",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v3basewalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3basewalletpoolposition",
            name="pending_inflator",
            field=models.DecimalField(decimal_places=18, max_digits=40, null=True),
        ),
        migrations.AlterField(
            model_name="v3ethereumcurrentwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3ethereumreserveauctionkick",
            name="kicker_award",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v3ethereumwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3ethereumwalletpoolposition",
            name="pending_inflator",
            field=models.DecimalField(decimal_places=18, max_digits=40, null=True),
        ),
        migrations.AlterField(
            model_name="v3goerlicurrentwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3goerlireserveauctionkick",
            name="kicker_award",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v3goerliwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3goerliwalletpoolposition",
            name="pending_inflator",
            field=models.DecimalField(decimal_places=18, max_digits=40, null=True),
        ),
        migrations.AlterField(
            model_name="v3optimismcurrentwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3optimismreserveauctionkick",
            name="kicker_award",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v3optimismwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3optimismwalletpoolposition",
            name="pending_inflator",
            field=models.DecimalField(decimal_places=18, max_digits=40, null=True),
        ),
        migrations.AlterField(
            model_name="v3polygoncurrentwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3polygonreserveauctionkick",
            name="kicker_award",
            field=models.DecimalField(decimal_places=18, max_digits=32, null=True),
        ),
        migrations.AlterField(
            model_name="v3polygonwalletpoolposition",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3polygonwalletpoolposition",
            name="pending_inflator",
            field=models.DecimalField(decimal_places=18, max_digits=40, null=True),
        ),
    ]
