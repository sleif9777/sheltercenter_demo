# Generated by Django 4.0 on 2022-04-28 04:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0031_alter_adopter_accept_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 4, 27)),
        ),
    ]
