# Generated by Django 4.0 on 2022-05-08 03:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wishlist', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dog',
            old_name='name',
            new_name='shelterluv_id',
        ),
    ]
