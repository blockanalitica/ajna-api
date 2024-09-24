# Generated by Django 5.1.1 on 2024-09-24 11:37

import django.contrib.postgres.fields
import django.core.serializers.json
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajna', '0098_alter_v2ethereumreserveauction_ajna_burned_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='V4RariActivitySnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('active_wallets', models.IntegerField()),
                ('total_wallets', models.IntegerField()),
                ('new_wallets', models.IntegerField()),
                ('active_this_month', models.IntegerField(null=True)),
                ('new_this_month', models.IntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariAuction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.TextField(unique=True)),
                ('pool_address', models.CharField(max_length=42)),
                ('borrower', models.CharField(max_length=42)),
                ('kicker', models.CharField(max_length=42, null=True)),
                ('collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('collateral_remaining', models.DecimalField(decimal_places=18, max_digits=32)),
                ('debt', models.DecimalField(decimal_places=18, max_digits=32)),
                ('debt_remaining', models.DecimalField(decimal_places=18, max_digits=32)),
                ('settled', models.BooleanField(default=False)),
                ('settle_time', models.DateTimeField(null=True)),
                ('bond_factor', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('bond_size', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('neutral_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('last_take_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariAuctionAuctionNFTSettle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_index', models.CharField(max_length=26, unique=True)),
                ('auction_uid', models.TextField()),
                ('pool_address', models.CharField(max_length=42)),
                ('borrower', models.CharField(max_length=42)),
                ('index', models.TextField()),
                ('collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('block_number', models.BigIntegerField()),
                ('block_datetime', models.DateTimeField()),
                ('transaction_hash', models.CharField(max_length=66, null=True)),
                ('collateral_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('quote_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
            ],
            options={
                'ordering': ('-block_number',),
                'get_latest_by': 'block_number',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariAuctionAuctionSettle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_index', models.CharField(max_length=26, unique=True)),
                ('auction_uid', models.TextField()),
                ('pool_address', models.CharField(max_length=42)),
                ('borrower', models.CharField(max_length=42)),
                ('collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('block_number', models.BigIntegerField()),
                ('block_datetime', models.DateTimeField()),
                ('transaction_hash', models.CharField(max_length=66, null=True)),
                ('collateral_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('quote_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
            ],
            options={
                'ordering': ('-block_number',),
                'get_latest_by': 'block_number',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariAuctionBucketTake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_index', models.CharField(max_length=26, unique=True)),
                ('auction_uid', models.TextField()),
                ('pool_address', models.CharField(max_length=42)),
                ('borrower', models.CharField(max_length=42)),
                ('taker', models.CharField(max_length=42)),
                ('index', models.BigIntegerField()),
                ('amount', models.DecimalField(decimal_places=18, max_digits=32)),
                ('collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('auction_price', models.DecimalField(decimal_places=18, max_digits=32)),
                ('bond_change', models.DecimalField(decimal_places=18, max_digits=32)),
                ('is_reward', models.BooleanField(default=False)),
                ('block_number', models.BigIntegerField()),
                ('block_datetime', models.DateTimeField()),
                ('transaction_hash', models.CharField(max_length=66, null=True)),
                ('collateral_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('quote_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
            ],
            options={
                'ordering': ('-block_number',),
                'get_latest_by': 'block_number',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariAuctionKick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_index', models.CharField(max_length=26, unique=True)),
                ('auction_uid', models.TextField()),
                ('pool_address', models.CharField(max_length=42)),
                ('borrower', models.CharField(max_length=42)),
                ('kicker', models.CharField(max_length=42)),
                ('debt', models.DecimalField(decimal_places=18, max_digits=32)),
                ('collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('bond', models.DecimalField(decimal_places=18, max_digits=32)),
                ('locked', models.DecimalField(decimal_places=18, max_digits=32)),
                ('kick_momp', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('reference_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('starting_price', models.DecimalField(decimal_places=18, max_digits=32)),
                ('block_number', models.BigIntegerField()),
                ('block_datetime', models.DateTimeField()),
                ('transaction_hash', models.CharField(max_length=66, null=True)),
                ('collateral_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('quote_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
            ],
            options={
                'ordering': ('-block_number',),
                'get_latest_by': 'block_number',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariAuctionSettle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_index', models.CharField(max_length=26, unique=True)),
                ('auction_uid', models.TextField()),
                ('pool_address', models.CharField(max_length=42)),
                ('borrower', models.CharField(max_length=42)),
                ('settled_debt', models.DecimalField(decimal_places=18, max_digits=32)),
                ('block_number', models.BigIntegerField()),
                ('block_datetime', models.DateTimeField()),
                ('transaction_hash', models.CharField(max_length=66, null=True)),
                ('collateral_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('quote_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
            ],
            options={
                'ordering': ('-block_number',),
                'get_latest_by': 'block_number',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariAuctionTake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_index', models.CharField(max_length=26, unique=True)),
                ('auction_uid', models.TextField()),
                ('pool_address', models.CharField(max_length=42)),
                ('borrower', models.CharField(max_length=42)),
                ('taker', models.CharField(max_length=42)),
                ('amount', models.DecimalField(decimal_places=18, max_digits=32)),
                ('collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('auction_price', models.DecimalField(decimal_places=18, max_digits=32)),
                ('bond_change', models.DecimalField(decimal_places=18, max_digits=32)),
                ('is_reward', models.BooleanField(default=False)),
                ('block_number', models.BigIntegerField()),
                ('block_datetime', models.DateTimeField()),
                ('transaction_hash', models.CharField(max_length=66, null=True)),
                ('collateral_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('quote_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
            ],
            options={
                'ordering': ('-block_number',),
                'get_latest_by': 'block_number',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariPool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('erc', models.CharField(choices=[('erc20', 'erc20'), ('erc721', 'erc721')], max_length=10, null=True)),
                ('pool_size', models.DecimalField(decimal_places=18, max_digits=32)),
                ('debt', models.DecimalField(decimal_places=18, max_digits=40)),
                ('t0debt', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('inflator', models.DecimalField(decimal_places=18, max_digits=32)),
                ('pending_inflator', models.DecimalField(decimal_places=18, max_digits=40, null=True)),
                ('borrow_rate', models.DecimalField(decimal_places=18, max_digits=32)),
                ('lend_rate', models.DecimalField(decimal_places=18, max_digits=40, null=True)),
                ('borrow_fee_rate', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('deposit_fee_rate', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('pledged_collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('total_interest_earned', models.DecimalField(decimal_places=18, max_digits=32)),
                ('tx_count', models.BigIntegerField(null=True)),
                ('loans_count', models.BigIntegerField()),
                ('max_borrower', models.CharField(max_length=42, null=True)),
                ('hpb', models.DecimalField(decimal_places=18, max_digits=32)),
                ('hpb_index', models.IntegerField()),
                ('htp', models.DecimalField(decimal_places=18, max_digits=32)),
                ('htp_index', models.IntegerField()),
                ('lup', models.DecimalField(decimal_places=18, max_digits=32)),
                ('lup_index', models.IntegerField()),
                ('momp', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('reserves', models.DecimalField(decimal_places=18, max_digits=32)),
                ('claimable_reserves', models.DecimalField(decimal_places=18, max_digits=32)),
                ('claimable_reserves_remaining', models.DecimalField(decimal_places=18, max_digits=32)),
                ('burn_epoch', models.BigIntegerField()),
                ('total_ajna_burned', models.DecimalField(decimal_places=18, default=Decimal('0'), max_digits=32)),
                ('min_debt_amount', models.DecimalField(decimal_places=18, max_digits=40)),
                ('utilization', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('current_meaningful_utilization', models.DecimalField(decimal_places=18, max_digits=40, null=True)),
                ('actual_utilization', models.DecimalField(decimal_places=18, max_digits=32)),
                ('target_utilization', models.DecimalField(decimal_places=18, max_digits=32)),
                ('total_bond_escrowed', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('quote_token_balance', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('collateral_token_balance', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('collateral_token_address', models.CharField(db_index=True, max_length=42, null=True)),
                ('quote_token_address', models.CharField(db_index=True, max_length=42, null=True)),
                ('volume_today', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('allowed_token_ids', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), null=True, size=None)),
                ('datetime', models.DateTimeField(db_index=True)),
                ('address', models.CharField(db_index=True, max_length=42, unique=True)),
                ('created_at_block_number', models.BigIntegerField()),
                ('created_at_timestamp', models.BigIntegerField()),
                ('last_block_number', models.BigIntegerField(null=True)),
                ('collateral_token_symbol', models.CharField(max_length=64, null=True)),
                ('quote_token_symbol', models.CharField(max_length=64, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariReserveAuction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.TextField(unique=True)),
                ('pool_address', models.CharField(max_length=42)),
                ('claimable_reserves', models.DecimalField(decimal_places=18, max_digits=64)),
                ('claimable_reserves_remaining', models.DecimalField(decimal_places=18, max_digits=64)),
                ('last_take_price', models.DecimalField(decimal_places=18, max_digits=64)),
                ('burn_epoch', models.BigIntegerField()),
                ('ajna_burned', models.DecimalField(decimal_places=18, max_digits=64)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariReserveAuctionKick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_index', models.CharField(max_length=26, unique=True)),
                ('reserve_auction_uid', models.TextField()),
                ('pool_address', models.CharField(max_length=42)),
                ('burn_epoch', models.BigIntegerField()),
                ('kicker', models.CharField(max_length=42)),
                ('kicker_award', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('claimable_reserves', models.DecimalField(decimal_places=18, max_digits=64)),
                ('starting_price', models.DecimalField(decimal_places=18, max_digits=64)),
                ('block_number', models.BigIntegerField()),
                ('block_datetime', models.DateTimeField()),
                ('transaction_hash', models.CharField(max_length=66)),
            ],
            options={
                'ordering': ('-block_number',),
                'get_latest_by': 'block_number',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariReserveAuctionTake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_index', models.CharField(max_length=26, unique=True)),
                ('reserve_auction_uid', models.TextField()),
                ('pool_address', models.CharField(max_length=42)),
                ('taker', models.CharField(max_length=42)),
                ('claimable_reserves_remaining', models.DecimalField(decimal_places=18, max_digits=64)),
                ('auction_price', models.DecimalField(decimal_places=18, max_digits=64)),
                ('ajna_burned', models.DecimalField(decimal_places=18, max_digits=64)),
                ('ajna_price', models.DecimalField(decimal_places=18, max_digits=64, null=True)),
                ('quote_purchased', models.DecimalField(decimal_places=18, max_digits=64)),
                ('block_number', models.BigIntegerField()),
                ('block_datetime', models.DateTimeField()),
                ('transaction_hash', models.CharField(max_length=66)),
            ],
            options={
                'ordering': ('-block_number',),
                'get_latest_by': 'block_number',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('underlying_address', models.CharField(db_index=True, max_length=42, unique=True)),
                ('symbol', models.CharField(db_index=True, max_length=64)),
                ('name', models.CharField(max_length=255)),
                ('decimals', models.BigIntegerField()),
                ('underlying_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('is_estimated_price', models.BooleanField(default=False)),
                ('pool_count', models.BigIntegerField(null=True)),
                ('total_supply', models.BigIntegerField(null=True)),
                ('tx_count', models.BigIntegerField(null=True)),
                ('is_erc721', models.BooleanField(null=True)),
                ('erc', models.CharField(choices=[('erc20', 'erc20'), ('erc721', 'erc721')], max_length=10, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariWallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=42, unique=True)),
                ('first_activity', models.DateTimeField(null=True)),
                ('last_activity', models.DateTimeField(null=True)),
                ('eoa', models.CharField(max_length=42, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='V4RariBucket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bucket_index', models.BigIntegerField()),
                ('bucket_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('exchange_rate', models.DecimalField(decimal_places=18, max_digits=32)),
                ('pool_address', models.CharField(db_index=True, max_length=42)),
                ('collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('deposit', models.DecimalField(decimal_places=18, max_digits=32)),
                ('lpb', models.DecimalField(decimal_places=18, max_digits=32)),
            ],
            options={
                'abstract': False,
                'unique_together': {('bucket_index', 'pool_address')},
            },
        ),
        migrations.CreateModel(
            name='V4RariCurrentWalletPoolPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet_address', models.CharField(db_index=True, max_length=42)),
                ('pool_address', models.CharField(db_index=True, max_length=42)),
                ('supply', models.DecimalField(decimal_places=18, max_digits=32)),
                ('collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('t0debt', models.DecimalField(decimal_places=18, max_digits=32)),
                ('debt', models.DecimalField(decimal_places=18, max_digits=40)),
                ('t0np', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('np_tp_ratio', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('in_liquidation', models.BooleanField(default=False)),
                ('datetime', models.DateTimeField()),
                ('block_number', models.BigIntegerField(db_index=True)),
            ],
            options={
                'ordering': ('block_number',),
                'get_latest_by': 'block_number',
                'abstract': False,
                'unique_together': {('wallet_address', 'block_number', 'pool_address')},
            },
        ),
        migrations.CreateModel(
            name='V4RariNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.TextField()),
                ('key', models.TextField()),
                ('data', models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('activity', models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder, null=True)),
                ('datetime', models.DateTimeField(db_index=True)),
                ('pool_address', models.CharField(max_length=42, null=True)),
            ],
            options={
                'ordering': ('-datetime',),
                'get_latest_by': 'datetime',
                'abstract': False,
                'unique_together': {('pool_address', 'key', 'type')},
            },
        ),
        migrations.CreateModel(
            name='V4RariPoolBucketState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pool_address', models.CharField(max_length=42)),
                ('bucket_index', models.IntegerField()),
                ('collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('deposit', models.DecimalField(decimal_places=18, max_digits=32)),
                ('bucket_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('exchange_rate', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('lpb', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('block_number', models.BigIntegerField()),
                ('block_datetime', models.DateTimeField()),
            ],
            options={
                'abstract': False,
                'indexes': [models.Index(fields=['pool_address', 'bucket_index', 'block_number'], name='ajna_v4rari_pool_ad_99525c_idx'), models.Index(fields=['pool_address', 'bucket_index'], name='ajna_v4rari_pool_ad_3db0af_idx'), models.Index(fields=['pool_address'], name='ajna_v4rari_pool_ad_6faeee_idx'), models.Index(fields=['bucket_index'], name='ajna_v4rari_bucket__f9b922_idx'), models.Index(fields=['block_number'], name='ajna_v4rari_block_n_667cc0_idx'), models.Index(fields=['block_datetime'], name='ajna_v4rari_block_d_870ea7_idx')],
                'unique_together': {('pool_address', 'bucket_index', 'block_number')},
            },
        ),
        migrations.CreateModel(
            name='V4RariPoolEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pool_address', models.CharField(max_length=42)),
                ('wallet_addresses', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=42), null=True, size=None)),
                ('bucket_indexes', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), null=True, size=None)),
                ('block_number', models.BigIntegerField()),
                ('block_datetime', models.DateTimeField()),
                ('order_index', models.CharField(max_length=26)),
                ('transaction_hash', models.CharField(max_length=66)),
                ('name', models.CharField(max_length=42)),
                ('data', models.JSONField()),
                ('collateral_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('quote_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
            ],
            options={
                'abstract': False,
                'indexes': [models.Index(fields=['pool_address', 'order_index'], name='ajna_v4rari_pool_ad_3e5db6_idx'), models.Index(fields=['pool_address', 'wallet_addresses', 'order_index'], name='ajna_v4rari_pool_ad_7a727c_idx'), models.Index(fields=['pool_address', 'wallet_addresses'], name='ajna_v4rari_pool_ad_f01655_idx'), models.Index(fields=['pool_address'], name='ajna_v4rari_pool_ad_cab171_idx'), models.Index(fields=['order_index'], name='ajna_v4rari_order_i_4df087_idx')],
                'unique_together': {('pool_address', 'order_index')},
            },
        ),
        migrations.CreateModel(
            name='V4RariPoolSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('erc', models.CharField(choices=[('erc20', 'erc20'), ('erc721', 'erc721')], max_length=10, null=True)),
                ('pool_size', models.DecimalField(decimal_places=18, max_digits=32)),
                ('debt', models.DecimalField(decimal_places=18, max_digits=40)),
                ('t0debt', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('inflator', models.DecimalField(decimal_places=18, max_digits=32)),
                ('pending_inflator', models.DecimalField(decimal_places=18, max_digits=40, null=True)),
                ('borrow_rate', models.DecimalField(decimal_places=18, max_digits=32)),
                ('lend_rate', models.DecimalField(decimal_places=18, max_digits=40, null=True)),
                ('borrow_fee_rate', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('deposit_fee_rate', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('pledged_collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('total_interest_earned', models.DecimalField(decimal_places=18, max_digits=32)),
                ('tx_count', models.BigIntegerField(null=True)),
                ('loans_count', models.BigIntegerField()),
                ('max_borrower', models.CharField(max_length=42, null=True)),
                ('hpb', models.DecimalField(decimal_places=18, max_digits=32)),
                ('hpb_index', models.IntegerField()),
                ('htp', models.DecimalField(decimal_places=18, max_digits=32)),
                ('htp_index', models.IntegerField()),
                ('lup', models.DecimalField(decimal_places=18, max_digits=32)),
                ('lup_index', models.IntegerField()),
                ('momp', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('reserves', models.DecimalField(decimal_places=18, max_digits=32)),
                ('claimable_reserves', models.DecimalField(decimal_places=18, max_digits=32)),
                ('claimable_reserves_remaining', models.DecimalField(decimal_places=18, max_digits=32)),
                ('burn_epoch', models.BigIntegerField()),
                ('total_ajna_burned', models.DecimalField(decimal_places=18, default=Decimal('0'), max_digits=32)),
                ('min_debt_amount', models.DecimalField(decimal_places=18, max_digits=40)),
                ('utilization', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('current_meaningful_utilization', models.DecimalField(decimal_places=18, max_digits=40, null=True)),
                ('actual_utilization', models.DecimalField(decimal_places=18, max_digits=32)),
                ('target_utilization', models.DecimalField(decimal_places=18, max_digits=32)),
                ('total_bond_escrowed', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('quote_token_balance', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('collateral_token_balance', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('collateral_token_address', models.CharField(db_index=True, max_length=42, null=True)),
                ('quote_token_address', models.CharField(db_index=True, max_length=42, null=True)),
                ('volume_today', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('allowed_token_ids', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), null=True, size=None)),
                ('datetime', models.DateTimeField(db_index=True)),
                ('address', models.CharField(db_index=True, max_length=42)),
                ('collateral_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('quote_token_price', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('collateralization', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
            ],
            options={
                'abstract': False,
                'indexes': [models.Index(fields=['address', 'datetime'], name='ajna_v4rari_address_3fac18_idx'), models.Index(fields=['datetime'], name='ajna_v4rari_datetim_6f1189_idx')],
                'unique_together': {('address', 'datetime')},
            },
        ),
        migrations.CreateModel(
            name='V4RariPoolVolumeSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pool_address', models.CharField(db_index=True, max_length=42)),
                ('amount', models.DecimalField(decimal_places=18, max_digits=32)),
                ('date', models.DateField()),
            ],
            options={
                'abstract': False,
                'unique_together': {('pool_address', 'date')},
            },
        ),
        migrations.CreateModel(
            name='V4RariPriceFeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=18, max_digits=32)),
                ('timestamp', models.BigIntegerField(db_index=True)),
                ('datetime', models.DateTimeField(null=True)),
                ('underlying_address', models.CharField(db_index=True, max_length=42)),
                ('estimated', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-datetime',),
                'get_latest_by': 'datetime',
                'abstract': False,
                'indexes': [models.Index(fields=['underlying_address'], name='ajna_v4rari_underly_607ab5_idx'), models.Index(fields=['timestamp'], name='ajna_v4rari_timesta_649dfa_idx'), models.Index(fields=['datetime'], name='ajna_v4rari_datetim_9891dd_idx'), models.Index(fields=['underlying_address', 'datetime'], name='ajna_v4rari_underly_4034c1_idx')],
            },
        ),
        migrations.CreateModel(
            name='V4RariWalletPoolBucketState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet_address', models.CharField(max_length=42)),
                ('pool_address', models.CharField(max_length=42)),
                ('bucket_index', models.IntegerField()),
                ('deposit', models.DecimalField(decimal_places=18, max_digits=32)),
                ('block_number', models.BigIntegerField()),
                ('block_datetime', models.DateTimeField()),
            ],
            options={
                'abstract': False,
                'indexes': [models.Index(fields=['pool_address', 'wallet_address', 'bucket_index', 'block_number'], name='ajna_v4rari_pool_ad_4cb984_idx'), models.Index(fields=['pool_address', 'wallet_address', 'bucket_index'], name='ajna_v4rari_pool_ad_ba1f3b_idx'), models.Index(fields=['pool_address'], name='ajna_v4rari_pool_ad_d517c4_idx'), models.Index(fields=['wallet_address'], name='ajna_v4rari_wallet__e233b7_idx'), models.Index(fields=['bucket_index'], name='ajna_v4rari_bucket__0457d3_idx'), models.Index(fields=['block_number'], name='ajna_v4rari_block_n_f2d701_idx'), models.Index(fields=['block_datetime'], name='ajna_v4rari_block_d_7f7765_idx')],
                'unique_together': {('pool_address', 'wallet_address', 'bucket_index', 'block_number')},
            },
        ),
        migrations.CreateModel(
            name='V4RariWalletPoolPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet_address', models.CharField(db_index=True, max_length=42)),
                ('pool_address', models.CharField(db_index=True, max_length=42)),
                ('supply', models.DecimalField(decimal_places=18, max_digits=32)),
                ('collateral', models.DecimalField(decimal_places=18, max_digits=32)),
                ('t0debt', models.DecimalField(decimal_places=18, max_digits=32)),
                ('debt', models.DecimalField(decimal_places=18, max_digits=40)),
                ('t0np', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('np_tp_ratio', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('in_liquidation', models.BooleanField(default=False)),
                ('pending_inflator', models.DecimalField(decimal_places=18, max_digits=40, null=True)),
                ('lup', models.DecimalField(decimal_places=18, max_digits=32, null=True)),
                ('datetime', models.DateTimeField()),
                ('block_number', models.BigIntegerField(db_index=True)),
            ],
            options={
                'ordering': ('block_number',),
                'get_latest_by': 'block_number',
                'abstract': False,
                'unique_together': {('wallet_address', 'block_number', 'pool_address')},
            },
        ),
    ]