# Generated by Django 4.0 on 2021-12-26 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_template', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='daily_schedule',
            name='bah',
            field=models.CharField(default='', max_length=2),
        ),
    ]
