# Generated by Django 4.0 on 2022-03-26 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_mgr', '0007_emailtemplate_plain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
