# Generated by Django 2.2.8 on 2020-05-23 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cost_per_action_type',
            name='cost_per_action_type_id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='cost_per_thruplay',
            name='cost_per_thruplay_id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
