# Generated by Django 4.0 on 2021-12-29 21:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0008_alter_adopter_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adopter',
            options={'ordering': ('adopter_last_name', 'adopter_first_name')},
        ),
    ]
