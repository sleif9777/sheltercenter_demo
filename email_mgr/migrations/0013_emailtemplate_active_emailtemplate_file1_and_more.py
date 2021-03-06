# Generated by Django 4.0 on 2022-05-22 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_mgr', '0012_emailtemplate_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='file1',
            field=models.FileField(blank=True, default=None, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='file2',
            field=models.FileField(blank=True, default=None, null=True, upload_to=''),
        ),
    ]
