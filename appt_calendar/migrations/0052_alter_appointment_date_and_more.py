# Generated by Django 4.0 on 2022-04-09 18:41

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0051_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 4, 9, 18, 41, 29, 8626, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(default=datetime.datetime(2022, 4, 9, 18, 41, 29, 8626, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 4, 9, 18, 41, 29, 9628, tzinfo=utc)),
        ),
    ]
