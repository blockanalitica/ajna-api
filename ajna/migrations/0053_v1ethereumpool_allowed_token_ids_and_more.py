# Generated by Django 4.2.3 on 2023-10-19 10:39

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ajna", "0052_v1ethereumpool_erc_v1ethereumpoolsnapshot_erc_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="v1ethereumpool",
            name="allowed_token_ids",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), null=True, size=None
            ),
        ),
        migrations.AddField(
            model_name="v1ethereumpoolsnapshot",
            name="allowed_token_ids",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), null=True, size=None
            ),
        ),
        migrations.AddField(
            model_name="v1goerlipool",
            name="allowed_token_ids",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), null=True, size=None
            ),
        ),
        migrations.AddField(
            model_name="v1goerlipoolsnapshot",
            name="allowed_token_ids",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), null=True, size=None
            ),
        ),
        migrations.AddField(
            model_name="v2ethereumpool",
            name="allowed_token_ids",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), null=True, size=None
            ),
        ),
        migrations.AddField(
            model_name="v2ethereumpoolsnapshot",
            name="allowed_token_ids",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), null=True, size=None
            ),
        ),
        migrations.AddField(
            model_name="v2goerlipool",
            name="allowed_token_ids",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), null=True, size=None
            ),
        ),
        migrations.AddField(
            model_name="v2goerlipoolsnapshot",
            name="allowed_token_ids",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), null=True, size=None
            ),
        ),
    ]
