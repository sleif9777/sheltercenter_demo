# Generated by Django 4.0 on 2022-04-05 03:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0022_adopter_carryover_shelterluv'),
    ]

    operations = [
        migrations.AddField(
            model_name='adopter',
            name='secondary_email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 4, 4)),
        ),
    ]
