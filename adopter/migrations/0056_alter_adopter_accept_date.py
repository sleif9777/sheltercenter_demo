# Generated by Django 4.1 on 2022-11-21 05:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0055_alter_adopter_accept_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 11, 21)),
        ),
    ]