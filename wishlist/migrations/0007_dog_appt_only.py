# Generated by Django 4.0 on 2022-07-31 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wishlist', '0006_dog_foster_date_dog_host_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='dog',
            name='appt_only',
            field=models.BooleanField(default=False),
        ),
    ]
