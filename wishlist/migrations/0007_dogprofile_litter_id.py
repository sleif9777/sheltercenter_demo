# Generated by Django 4.1 on 2023-01-07 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wishlist', '0006_dogprofile_update_dt'),
    ]

    operations = [
        migrations.AddField(
            model_name='dogprofile',
            name='litter_id',
            field=models.CharField(default=None, max_length=20, null=True, blank=True),
        ),
    ]