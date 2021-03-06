# Generated by Django 4.0 on 2022-04-30 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_mgr', '0010_delete_emailtemplate2_remove_emailtemplate_plain'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(default='', max_length=300)),
                ('text', models.TextField(blank=True, default='')),
                ('html', models.TextField(blank=True, default='')),
                ('email', models.EmailField(default='', max_length=254)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
    ]
