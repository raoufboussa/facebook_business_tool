# Generated by Django 2.2.8 on 2020-05-23 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_auth', '0002_auto_20200523_0233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cost_per_action_type',
            name='action_type',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='cost_per_action_type',
            name='value',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='cost_per_thruplay',
            name='action_type',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='cost_per_thruplay',
            name='value',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
