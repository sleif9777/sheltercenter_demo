# Generated by Django 2.0.2 on 2021-12-05 22:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0002_adopter_acknowledged_faq'),
        ('appt_calendar', '0008_auto_20211205_2138'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='adopter_choice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adopter.Adopter'),
        ),
    ]