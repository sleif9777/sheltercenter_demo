# Generated by Django 4.0 on 2022-08-07 17:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_template', '0031_alter_systemsettings_last_adopter_upload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemsettings',
            name='last_adopter_upload',
            field=models.DateField(default=datetime.date(2022, 8, 7)),
        ),
    ]
