# Generated by Django 4.0 on 2022-04-12 12:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0030_alter_adopter_app_interest_alter_adopter_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 4, 12)),
        ),
    ]
