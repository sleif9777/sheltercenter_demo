# Generated by Django 4.0 on 2022-03-10 05:53

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0024_alter_appointment_date_alter_timeslot_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 3, 10, 5, 53, 3, 889927, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 3, 10, 5, 53, 3, 894867, tzinfo=utc)),
        ),
    ]
