# Generated by Django 4.1 on 2022-11-24 18:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0124_appointment_counselor_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 11, 24, 18, 38, 46, 352028, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 11, 24, 18, 38, 46, 352123, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='dailyannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 11, 24, 18, 38, 46, 351428, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='internalannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 11, 24, 18, 38, 46, 351801, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='shortnotice',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 11, 24, 18, 38, 46, 352697, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 11, 24, 18, 38, 46, 352393, tzinfo=datetime.timezone.utc)),
        ),
    ]
