<<<<<<< HEAD
# Generated by Django 4.0 on 2022-08-07 17:38
=======
# Generated by Django 4.0 on 2022-08-14 16:25
>>>>>>> apptdogs

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0050_alter_adopter_accept_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
<<<<<<< HEAD
            field=models.DateField(blank=True, default=datetime.date(2022, 8, 7)),
=======
            field=models.DateField(blank=True, default=datetime.date(2022, 8, 14)),
>>>>>>> apptdogs
        ),
    ]
