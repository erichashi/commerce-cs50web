# Generated by Django 3.0.8 on 2020-08-15 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20200814_2114'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auctionlisting',
            name='isWatch',
        ),
    ]
