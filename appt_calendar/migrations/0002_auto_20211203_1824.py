# Generated by Django 2.0.2 on 2021-12-03 18:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.date(2021, 12, 3)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.date(2021, 12, 3)),
        ),
    ]
