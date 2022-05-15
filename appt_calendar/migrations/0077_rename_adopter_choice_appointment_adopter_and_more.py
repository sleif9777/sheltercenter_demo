# Generated by Django 4.0 on 2022-05-07 22:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0076_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='adopter_choice',
            new_name='adopter',
        ),
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 5, 7, 22, 20, 17, 702899, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 5, 7, 22, 20, 17, 702899, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='dailyannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 5, 7, 22, 20, 17, 701743, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 5, 7, 22, 20, 17, 703738, tzinfo=utc)),
        ),
    ]