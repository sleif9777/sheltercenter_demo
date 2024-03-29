# Generated by Django 4.1 on 2023-01-30 21:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0159_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 1, 30, 21, 21, 54, 726284, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2023, 1, 30, 21, 21, 54, 726407, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='dailyannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 1, 30, 21, 21, 54, 726039, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='internalannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 1, 30, 21, 21, 54, 726128, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='shortnotice',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 1, 30, 21, 21, 54, 726962, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 1, 30, 21, 21, 54, 726664, tzinfo=datetime.timezone.utc)),
        ),
    ]
