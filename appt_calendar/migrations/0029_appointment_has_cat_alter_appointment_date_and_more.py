# Generated by Django 4.0 on 2022-03-22 01:24

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0028_alter_appointment_date_alter_timeslot_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='has_cat',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 3, 22, 1, 24, 6, 949226, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 3, 22, 1, 24, 6, 951229, tzinfo=utc)),
        ),
    ]
