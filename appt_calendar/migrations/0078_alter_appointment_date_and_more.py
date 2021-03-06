# Generated by Django 4.0 on 2022-05-08 03:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0077_rename_adopter_choice_appointment_adopter_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 5, 8, 3, 14, 20, 330026, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 5, 8, 3, 14, 20, 331024, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='dailyannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 5, 8, 3, 14, 20, 329029, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 5, 8, 3, 14, 20, 332020, tzinfo=utc)),
        ),
    ]
