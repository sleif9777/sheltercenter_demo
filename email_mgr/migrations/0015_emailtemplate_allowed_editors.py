# Generated by Django 4.1 on 2023-01-17 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('email_mgr', '0014_alter_emailtemplate_file1_alter_emailtemplate_file2'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='allowed_editors',
            field=models.ManyToManyField(blank=True, null=True, to='auth.group'),
        ),
    ]