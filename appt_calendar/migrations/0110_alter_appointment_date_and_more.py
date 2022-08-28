# Generated by Django 4.1 on 2022-08-06 16:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0109_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 8, 6, 16, 56, 37, 820386, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 8, 6, 16, 56, 37, 820453, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='dailyannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 8, 6, 16, 56, 37, 819923, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='internalannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 8, 6, 16, 56, 37, 820233, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='shortnotice',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 8, 6, 16, 56, 37, 820967, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 8, 6, 16, 56, 37, 820654, tzinfo=datetime.timezone.utc)),
        ),
    ]
