# Generated by Django 4.1 on 2022-10-30 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_rename_adminprofile_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='ac_show_booking_timestamp',
            field=models.BooleanField(default=True),
        ),
    ]
