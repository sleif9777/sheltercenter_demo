# Generated by Django 4.1 on 2023-01-07 05:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0062_alter_adopter_wishlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2023, 1, 7)),
        ),
        migrations.AlterField(
            model_name='adopter',
            name='alert_date',
            field=models.DateField(blank=True, default=datetime.date(2023, 1, 1)),
        ),
        migrations.AlterField(
            model_name='adopter',
            name='max_weight',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='adopter',
            name='min_weight',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
