# Generated by Django 4.0 on 2022-04-03 18:10

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0044_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='visits_to_date',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 4, 3, 18, 10, 48, 623471, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(default=datetime.datetime(2022, 4, 3, 18, 10, 48, 624470, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 4, 3, 18, 10, 48, 624470, tzinfo=utc)),
        ),
    ]
