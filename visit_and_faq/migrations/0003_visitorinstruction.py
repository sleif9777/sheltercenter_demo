# Generated by Django 4.0 on 2022-04-10 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visit_and_faq', '0002_alter_faqsection_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitorInstruction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(default='', max_length=500)),
                ('text', models.TextField(default='')),
                ('order', models.IntegerField(default=1)),
            ],
            options={
                'ordering': ('order', 'id', 'header'),
            },
        ),
    ]
