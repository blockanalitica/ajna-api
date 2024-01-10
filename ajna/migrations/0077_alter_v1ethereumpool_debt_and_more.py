# Generated by Django 4.2.3 on 2024-01-08 13:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0076_alter_v1ethereumpool_pending_inflator_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="v1ethereumpool",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v1ethereumpoolsnapshot",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v1goerlipool",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v1goerlipoolsnapshot",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v2ethereumpool",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v2ethereumpoolsnapshot",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v2goerlipool",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v2goerlipoolsnapshot",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3arbitrumpool",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3arbitrumpoolsnapshot",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3basepool",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3basepoolsnapshot",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3ethereumpool",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3ethereumpoolsnapshot",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3goerlipool",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3goerlipoolsnapshot",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3optimismpool",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3optimismpoolsnapshot",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3polygonpool",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
        migrations.AlterField(
            model_name="v3polygonpoolsnapshot",
            name="debt",
            field=models.DecimalField(decimal_places=18, max_digits=40),
        ),
    ]