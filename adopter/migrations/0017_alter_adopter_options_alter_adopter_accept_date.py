# Generated by Django 4.0 on 2022-03-25 23:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0016_alter_adopter_accept_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adopter',
            options={'ordering': ('adopter_first_name', 'adopter_last_name')},
        ),
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 3, 25)),
        ),
    ]
