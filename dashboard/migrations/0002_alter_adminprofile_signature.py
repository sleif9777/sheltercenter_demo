# Generated by Django 4.0 on 2022-04-10 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminprofile',
            name='signature',
            field=models.TextField(default=''),
        ),
    ]