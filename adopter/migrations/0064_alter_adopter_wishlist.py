# Generated by Django 4.1 on 2023-01-07 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wishlist', '0008_dogobject_litterobject_delete_dogprofile'),
        ('adopter', '0063_alter_adopter_accept_date_alter_adopter_alert_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adopter',
            name='wishlist',
            field=models.ManyToManyField(blank=True, null=True, to='wishlist.dogobject'),
        ),
    ]
