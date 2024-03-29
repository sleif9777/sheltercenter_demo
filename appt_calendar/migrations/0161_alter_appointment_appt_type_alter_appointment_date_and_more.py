# Generated by Django 4.1 on 2023-02-02 22:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0160_alter_appointment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='appt_type',
            field=models.CharField(choices=[('1', 'Adults'), ('2', 'Puppies'), ('3', 'Puppies and/or Adults'), ('4', 'Surrender'), ('5', 'Adoption Paperwork'), ('6', 'FTA Paperwork'), ('7', 'Visit'), ('8', 'Donation Drop-Off'), ('9', 'Host Weekend/Chosen')], default='1', max_length=1),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 2, 2, 22, 51, 10, 720584, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2023, 2, 2, 22, 51, 10, 720707, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='dailyannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 2, 2, 22, 51, 10, 720347, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='internalannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 2, 2, 22, 51, 10, 720439, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='shortnotice',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 2, 2, 22, 51, 10, 721227, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 2, 2, 22, 51, 10, 720952, tzinfo=datetime.timezone.utc)),
        ),
    ]
