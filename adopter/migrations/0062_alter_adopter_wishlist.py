# Generated by Django 4.1 on 2022-12-24 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wishlist', '0005_dogprofile'),
        ('adopter', '0061_alter_adopter_accept_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adopter',
            name='wishlist',
            field=models.ManyToManyField(blank=True, null=True, to='wishlist.dogprofile'),
        ),
    ]