# Generated by Django 2.2.8 on 2020-07-08 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_auth', '0020_experience_campaign'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='location',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
