# Generated by Django 5.0.6 on 2024-05-28 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajna', '0091_v4modeauction_v4modeauctionauctionnftsettle_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='v2ethereumpoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v2ethe_address_e10b82_idx'),
        ),
        migrations.AddIndex(
            model_name='v2ethereumpoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v2ethe_datetim_6e1c79_idx'),
        ),
        migrations.AddIndex(
            model_name='v3arbitrumpoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v3arbi_address_76e94f_idx'),
        ),
        migrations.AddIndex(
            model_name='v3arbitrumpoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v3arbi_datetim_d7e7b9_idx'),
        ),
        migrations.AddIndex(
            model_name='v3basepoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v3base_address_84945e_idx'),
        ),
        migrations.AddIndex(
            model_name='v3basepoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v3base_datetim_f7808a_idx'),
        ),
        migrations.AddIndex(
            model_name='v3ethereumpoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v3ethe_address_108e64_idx'),
        ),
        migrations.AddIndex(
            model_name='v3ethereumpoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v3ethe_datetim_d6b049_idx'),
        ),
        migrations.AddIndex(
            model_name='v3optimismpoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v3opti_address_63b4c7_idx'),
        ),
        migrations.AddIndex(
            model_name='v3optimismpoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v3opti_datetim_203926_idx'),
        ),
        migrations.AddIndex(
            model_name='v3polygonpoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v3poly_address_fb2260_idx'),
        ),
        migrations.AddIndex(
            model_name='v3polygonpoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v3poly_datetim_be49bb_idx'),
        ),
        migrations.AddIndex(
            model_name='v4arbitrumpoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v4arbi_address_5f3fa5_idx'),
        ),
        migrations.AddIndex(
            model_name='v4arbitrumpoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v4arbi_datetim_f1b0e9_idx'),
        ),
        migrations.AddIndex(
            model_name='v4basepoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v4base_address_efc9e6_idx'),
        ),
        migrations.AddIndex(
            model_name='v4basepoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v4base_datetim_c1d4a3_idx'),
        ),
        migrations.AddIndex(
            model_name='v4blastpoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v4blas_address_40535c_idx'),
        ),
        migrations.AddIndex(
            model_name='v4blastpoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v4blas_datetim_86f914_idx'),
        ),
        migrations.AddIndex(
            model_name='v4gnosispoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v4gnos_address_7e9dff_idx'),
        ),
        migrations.AddIndex(
            model_name='v4gnosispoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v4gnos_datetim_18a54e_idx'),
        ),
        migrations.AddIndex(
            model_name='v4modepoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v4mode_address_aa5927_idx'),
        ),
        migrations.AddIndex(
            model_name='v4modepoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v4mode_datetim_2a4e1e_idx'),
        ),
        migrations.AddIndex(
            model_name='v4optimismpoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v4opti_address_e15ac8_idx'),
        ),
        migrations.AddIndex(
            model_name='v4optimismpoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v4opti_datetim_fd0b19_idx'),
        ),
        migrations.AddIndex(
            model_name='v4polygonpoolsnapshot',
            index=models.Index(fields=['address', 'datetime'], name='ajna_v4poly_address_a3e048_idx'),
        ),
        migrations.AddIndex(
            model_name='v4polygonpoolsnapshot',
            index=models.Index(fields=['datetime'], name='ajna_v4poly_datetim_71d90f_idx'),
        ),
    ]
