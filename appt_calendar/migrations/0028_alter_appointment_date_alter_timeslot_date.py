# Generated by Django 4.0 on 2022-03-22 00:37

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0027_alter_appointment_date_alter_timeslot_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 3, 22, 0, 37, 41, 211550, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 3, 22, 0, 37, 41, 213586, tzinfo=utc)),
        ),
    ]
