# Generated by Django 4.0 on 2021-12-29 21:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_template', '0002_daily_schedule_bah'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='daily_schedule',
            name='bah',
        ),
    ]
