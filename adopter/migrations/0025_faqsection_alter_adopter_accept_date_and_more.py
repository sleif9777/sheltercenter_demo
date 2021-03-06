# Generated by Django 4.0 on 2022-04-09 18:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0024_adopter_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='adopter',
            name='accept_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 4, 9)),
        ),
        migrations.AlterField(
            model_name='adopter',
            name='alert_date',
            field=models.DateField(blank=True, default=datetime.date(2022, 1, 1)),
        ),
    ]
