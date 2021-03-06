# Generated by Django 4.0 on 2022-07-02 16:13

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0095_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shortnotice',
            name='dog',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 2, 16, 13, 48, 707035, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 7, 2, 16, 13, 48, 708031, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='dailyannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 2, 16, 13, 48, 706005, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='internalannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 2, 16, 13, 48, 707035, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='shortnotice',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 2, 16, 13, 48, 709028, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 2, 16, 13, 48, 708031, tzinfo=utc)),
        ),
    ]
