# Generated by Django 4.0 on 2022-04-03 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0021_alter_adopter_accept_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='adopter',
            name='carryover_shelterluv',
            field=models.BooleanField(default=False),
        ),
    ]
