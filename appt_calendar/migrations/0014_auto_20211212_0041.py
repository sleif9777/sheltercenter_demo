# Generated by Django 2.0.2 on 2021-12-12 00:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0013_auto_20211211_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='heartworm',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.date(2021, 12, 12)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='outcome',
            field=models.CharField(choices=[('1', 'NA'), ('2', 'Adoption'), ('3', 'Chosen'), ('4', 'FTA'), ('5', 'No Decision'), ('6', 'Ready To Roll')], default='6', max_length=1),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.date(2021, 12, 12)),
        ),
    ]
