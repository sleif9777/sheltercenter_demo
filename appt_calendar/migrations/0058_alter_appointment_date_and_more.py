# Generated by Django 4.0 on 2022-04-10 19:38

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0057_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 4, 10, 19, 38, 7, 791402, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(default=datetime.datetime(2022, 4, 10, 19, 38, 7, 791402, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 4, 10, 19, 38, 7, 793397, tzinfo=utc)),
        ),
    ]