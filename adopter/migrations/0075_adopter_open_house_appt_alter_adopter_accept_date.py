# Generated by Django 4.1 on 2023-02-11 05:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0074_alter_adopter_accept_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='adopter',
            name='open_house_appt',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2023, 2, 11)),
        ),
    ]