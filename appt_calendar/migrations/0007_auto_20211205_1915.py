# Generated by Django 2.0.2 on 2021-12-05 19:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0006_auto_20211204_0153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.date(2021, 12, 5)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.date(2021, 12, 5)),
        ),
    ]
