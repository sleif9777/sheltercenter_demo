# Generated by Django 4.0 on 2022-03-26 04:59

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('email_mgr', '0004_emailtemplate2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name='text',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
    ]