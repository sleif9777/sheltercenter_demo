# Generated by Django 4.1 on 2022-12-20 18:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_template', '0038_alter_systemsettings_last_adopter_upload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemsettings',
            name='last_adopter_upload',
            field=models.DateField(default=datetime.date(2022, 12, 20)),
        ),
    ]
