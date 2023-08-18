# Generated by Django 4.1 on 2023-02-02 22:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_template', '0051_alter_systemsettings_last_adopter_upload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointmenttemplate',
            name='appt_type',
            field=models.CharField(choices=[('1', 'Adults'), ('2', 'Puppies'), ('3', 'Puppies and/or Adults'), ('4', 'Surrender'), ('5', 'Adoption'), ('6', 'FTA'), ('7', 'Visit'), ('8', 'Donation Drop-Off'), ('9', 'Host Weekend/Chosen')], default='1', max_length=1),
        ),
        migrations.AlterField(
            model_name='systemsettings',
            name='last_adopter_upload',
            field=models.DateField(default=datetime.date(2023, 2, 2)),
        ),
    ]
