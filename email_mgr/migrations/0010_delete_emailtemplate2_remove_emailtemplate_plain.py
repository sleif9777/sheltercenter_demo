# Generated by Django 4.0 on 2022-04-04 03:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_mgr', '0009_alter_emailtemplate_options_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EmailTemplate2',
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='plain',
        ),
    ]