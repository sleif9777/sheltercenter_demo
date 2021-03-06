# Generated by Django 4.0 on 2022-04-28 04:06

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0064_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyAnnouncement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime(2022, 4, 28, 4, 6, 33, 582602, tzinfo=utc))),
                ('text', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 4, 28, 4, 6, 33, 583600, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 4, 28, 4, 6, 33, 583600, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 4, 28, 4, 6, 33, 584596, tzinfo=utc)),
        ),
    ]
