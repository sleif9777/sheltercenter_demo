# Generated by Django 4.1 on 2022-09-05 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0052_adopter_requested_access_alter_adopter_accept_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='adopter',
            name='requested_surrender',
            field=models.BooleanField(default=False),
        ),
    ]
