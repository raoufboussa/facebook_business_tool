# Generated by Django 2.2.8 on 2020-06-14 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_auth', '0011_account_page_posts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='shares',
            field=models.IntegerField(default=0),
        ),
    ]
