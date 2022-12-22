# Generated by Django 4.1 on 2022-12-22 00:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0128_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='comm_dog_is_popular_low_chances',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appointment',
            name='comm_dog_not_here_yet',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 12, 22, 0, 14, 39, 69702, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 12, 22, 0, 14, 39, 69786, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='dailyannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 12, 22, 0, 14, 39, 69399, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='internalannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 12, 22, 0, 14, 39, 69498, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='shortnotice',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 12, 22, 0, 14, 39, 70303, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 12, 22, 0, 14, 39, 70033, tzinfo=datetime.timezone.utc)),
        ),
    ]
