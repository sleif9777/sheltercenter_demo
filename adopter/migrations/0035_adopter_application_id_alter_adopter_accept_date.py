# Generated by Django 4.0 on 2022-04-30 07:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0034_alter_adopter_accept_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='adopter',
            name='application_id',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 4, 30)),
        ),
    ]
