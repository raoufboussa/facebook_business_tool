# Generated by Django 2.2.8 on 2020-06-14 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_auth', '0010_auto_20200614_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='account_page',
            name='posts',
            field=models.ManyToManyField(to='facebook_auth.Post'),
        ),
    ]
