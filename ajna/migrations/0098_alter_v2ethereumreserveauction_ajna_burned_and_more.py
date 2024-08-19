# Generated by Django 5.0.6 on 2024-08-08 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajna', '0097_alter_v2ethereumreserveauctionkick_claimable_reserves_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='v2ethereumreserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v2ethereumreserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v2ethereumreserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v2ethereumreserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v2ethereumreserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v2ethereumreserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v2ethereumreserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v2ethereumreserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v2ethereumreserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3arbitrumreserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3arbitrumreserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3arbitrumreserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3arbitrumreserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3arbitrumreserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3arbitrumreserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v3arbitrumreserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3arbitrumreserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3arbitrumreserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3basereserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3basereserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3basereserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3basereserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3basereserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3basereserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v3basereserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3basereserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3basereserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3ethereumreserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3ethereumreserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3ethereumreserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3ethereumreserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3ethereumreserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3ethereumreserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v3ethereumreserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3ethereumreserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3ethereumreserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3optimismreserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3optimismreserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3optimismreserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3optimismreserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3optimismreserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3optimismreserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v3optimismreserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3optimismreserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3optimismreserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3polygonreserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3polygonreserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3polygonreserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3polygonreserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3polygonreserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3polygonreserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v3polygonreserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3polygonreserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v3polygonreserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4arbitrumreserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4arbitrumreserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4arbitrumreserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4arbitrumreserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4arbitrumreserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4arbitrumreserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v4arbitrumreserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4arbitrumreserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4arbitrumreserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4basereserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4basereserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4basereserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4basereserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4basereserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4basereserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v4basereserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4basereserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4basereserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4blastreserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4blastreserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4blastreserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4blastreserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4blastreserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4blastreserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v4blastreserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4blastreserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4blastreserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4gnosisreserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4gnosisreserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4gnosisreserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4gnosisreserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4gnosisreserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4gnosisreserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v4gnosisreserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4gnosisreserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4gnosisreserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4modereserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4modereserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4modereserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4modereserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4modereserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4modereserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v4modereserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4modereserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4modereserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4optimismreserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4optimismreserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4optimismreserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4optimismreserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4optimismreserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4optimismreserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v4optimismreserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4optimismreserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4optimismreserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4polygonreserveauction',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4polygonreserveauction',
            name='claimable_reserves',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4polygonreserveauction',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4polygonreserveauction',
            name='last_take_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4polygonreserveauctiontake',
            name='ajna_burned',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4polygonreserveauctiontake',
            name='ajna_price',
            field=models.DecimalField(decimal_places=18, max_digits=64, null=True),
        ),
        migrations.AlterField(
            model_name='v4polygonreserveauctiontake',
            name='auction_price',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4polygonreserveauctiontake',
            name='claimable_reserves_remaining',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
        migrations.AlterField(
            model_name='v4polygonreserveauctiontake',
            name='quote_purchased',
            field=models.DecimalField(decimal_places=18, max_digits=64),
        ),
    ]