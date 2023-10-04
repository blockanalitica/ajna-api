# Generated by Django 4.2.3 on 2023-10-04 09:18

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0037_v1ethereumpool_volume_today_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="v2ethereumnotification",
            options={"get_latest_by": "datetime", "ordering": ("-datetime",)},
        ),
        migrations.AlterModelOptions(
            name="v2goerlinotification",
            options={"get_latest_by": "datetime", "ordering": ("-datetime",)},
        ),
        migrations.AddField(
            model_name="v2ethereumnotification",
            name="datetime",
            field=models.DateTimeField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="v2goerlinotification",
            name="datetime",
            field=models.DateTimeField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name="v2ethereumnotification",
            name="activity",
            field=models.JSONField(
                encoder=django.core.serializers.json.DjangoJSONEncoder, null=True
            ),
        ),
        migrations.AlterField(
            model_name="v2ethereumnotification",
            name="data",
            field=models.JSONField(
                encoder=django.core.serializers.json.DjangoJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="v2goerlinotification",
            name="activity",
            field=models.JSONField(
                encoder=django.core.serializers.json.DjangoJSONEncoder, null=True
            ),
        ),
        migrations.AlterField(
            model_name="v2goerlinotification",
            name="data",
            field=models.JSONField(
                encoder=django.core.serializers.json.DjangoJSONEncoder
            ),
        ),
    ]
