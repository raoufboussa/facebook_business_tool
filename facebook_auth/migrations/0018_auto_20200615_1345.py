# Generated by Django 2.2.8 on 2020-06-15 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_auth', '0017_auto_20200614_2015'),
    ]

    operations = [
        migrations.AddField(
            model_name='account_page',
            name='last_update',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='ad_account',
            name='last_update',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='ad_account',
            name='last_update_campaigns_insights',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
