# Generated by Django 4.1 on 2022-11-24 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_profile_ac_show_adopter_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='ac_show_counselor',
            field=models.BooleanField(default=True),
        ),
    ]
