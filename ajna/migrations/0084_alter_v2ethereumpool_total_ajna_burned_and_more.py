# Generated by Django 4.2.3 on 2024-01-18 13:04

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0083_alter_v2ethereumpool_current_meaningful_utilization_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="v2ethereumpool",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v2ethereumpoolsnapshot",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v2goerlipool",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v2goerlipoolsnapshot",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3arbitrumpool",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3arbitrumpoolsnapshot",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3basepool",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3basepoolsnapshot",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3ethereumpool",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3ethereumpoolsnapshot",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3goerlipool",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3goerlipoolsnapshot",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3optimismpool",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3optimismpoolsnapshot",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3polygonpool",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
        migrations.AlterField(
            model_name="v3polygonpoolsnapshot",
            name="total_ajna_burned",
            field=models.DecimalField(
                decimal_places=18, default=Decimal("0"), max_digits=32
            ),
        ),
    ]
