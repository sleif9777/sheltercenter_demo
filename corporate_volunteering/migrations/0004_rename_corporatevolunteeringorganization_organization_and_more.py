# Generated by Django 4.1 on 2023-01-10 04:50

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('corporate_volunteering', '0003_remove_corporatevolunteeringevent_org_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CorporateVolunteeringOrganization',
            new_name='Organization',
        ),
        migrations.RenameModel(
            old_name='CorporateVolunteeringEvent',
            new_name='VolunteeringEvent',
        ),
    ]