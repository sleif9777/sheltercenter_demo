# Generated by Django 2.0.2 on 2021-12-03 19:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appt_calendar', '0003_appointment_adopter_choice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='adopter_email',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='adopter_first_name',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='adopter_last_name',
        ),
    ]
