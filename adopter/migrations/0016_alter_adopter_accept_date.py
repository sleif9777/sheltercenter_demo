# Generated by Django 4.0 on 2022-03-24 19:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0015_alter_adopter_accept_date_alter_adopter_auth_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 3, 24)),
        ),
    ]
