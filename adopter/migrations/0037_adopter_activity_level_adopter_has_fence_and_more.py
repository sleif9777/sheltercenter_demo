# Generated by Django 4.0 on 2022-04-30 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0036_adopter_city_adopter_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='adopter',
            name='activity_level',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='adopter',
            name='has_fence',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='adopter',
            name='housing',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='adopter',
            name='housing_type',
            field=models.CharField(default='', max_length=200),
        ),
    ]
