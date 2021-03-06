# Generated by Django 4.0 on 2022-04-11 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0029_alter_adopter_accept_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adopter',
            name='app_interest',
            field=models.CharField(blank=True, default='', max_length=2000),
        ),
        migrations.AlterField(
            model_name='adopter',
            name='status',
            field=models.CharField(choices=[('1', 'Approved'), ('2', 'Blocked'), ('3', 'Pending')], default='1', max_length=1),
        ),
    ]
