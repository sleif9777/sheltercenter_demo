# Generated by Django 4.0 on 2022-07-01 23:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0043_adopter_age_preference_adopter_gender_preference_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 7, 1)),
        ),
    ]