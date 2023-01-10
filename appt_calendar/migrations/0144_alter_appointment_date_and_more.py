# Generated by Django 4.1 on 2023-01-09 05:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0143_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 1, 9, 5, 39, 1, 979724, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2023, 1, 9, 5, 39, 1, 979816, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='dailyannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 1, 9, 5, 39, 1, 979476, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='internalannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 1, 9, 5, 39, 1, 979570, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='shortnotice',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 1, 9, 5, 39, 1, 980411, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 1, 9, 5, 39, 1, 980122, tzinfo=datetime.timezone.utc)),
        ),
    ]