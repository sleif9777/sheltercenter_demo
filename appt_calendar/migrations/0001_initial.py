# Generated by Django 2.0.2 on 2021-12-02 22:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date(2021, 12, 2))),
                ('time', models.TimeField(default=datetime.time(12, 0))),
                ('appt_type', models.CharField(choices=[('1', 'Adults'), ('2', 'Puppies'), ('3', 'Puppies or Adults'), ('4', 'Surrender'), ('5', 'Adoption Paperwork'), ('6', 'FTA Paperwork')], default='1', max_length=1)),
                ('adopter_first_name', models.CharField(blank=True, default='', max_length=200)),
                ('adopter_last_name', models.CharField(blank=True, default='', max_length=200)),
                ('adopter_email', models.EmailField(blank=True, default='', max_length=254)),
                ('available', models.BooleanField()),
                ('published', models.BooleanField()),
                ('dog', models.CharField(blank=True, default='', max_length=200)),
                ('dog_fka', models.CharField(blank=True, default='', max_length=200)),
                ('internal_notes', models.TextField(blank=True, default='')),
            ],
            options={
                'ordering': ('time', 'appt_type'),
            },
        ),
        migrations.CreateModel(
            name='Timeslot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date(2021, 12, 2))),
                ('time', models.TimeField(default=datetime.time(12, 0))),
                ('appointments', models.ManyToManyField(blank=True, to='appt_calendar.Appointment')),
            ],
            options={
                'ordering': ('time',),
            },
        ),
    ]
