# Generated by Django 4.0 on 2022-03-18 04:06

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0013_adopter_status_alter_adopter_accept_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='adopter',
            name='auth_code',
            field=models.IntegerField(default=100000, validators=[django.core.validators.MinValueValidator(100001), django.core.validators.MaxValueValidator(999999)]),
        ),
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 3, 17)),
        ),
    ]