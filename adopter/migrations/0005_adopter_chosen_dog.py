# Generated by Django 2.0.2 on 2021-12-09 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0004_auto_20211209_2242'),
    ]

    operations = [
        migrations.AddField(
            model_name='adopter',
            name='chosen_dog',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
