# Generated by Django 4.0 on 2022-05-08 04:25

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0082_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 5, 8, 4, 25, 21, 351887, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 5, 8, 4, 25, 21, 352844, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='dailyannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 5, 8, 4, 25, 21, 350889, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 5, 8, 4, 25, 21, 354604, tzinfo=utc)),
        ),
    ]
