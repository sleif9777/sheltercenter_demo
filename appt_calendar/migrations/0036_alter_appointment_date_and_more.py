# Generated by Django 4.0 on 2022-03-26 00:45

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0035_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 3, 26, 0, 45, 47, 481494, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(default=datetime.datetime(2022, 3, 26, 0, 45, 47, 481494, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 3, 26, 0, 45, 47, 483558, tzinfo=utc)),
        ),
    ]
