# Generated by Django 4.0 on 2022-07-02 01:01

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('adopter', '0044_alter_adopter_accept_date'),
        ('appt_calendar', '0094_rename_late_notice_appointment_short_notice_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 2, 1, 1, 2, 710353, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='last_update_sent',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 7, 2, 1, 1, 2, 710353, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='dailyannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 2, 1, 1, 2, 709357, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='internalannouncement',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 2, 1, 1, 2, 709357, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 2, 1, 1, 2, 711320, tzinfo=utc)),
        ),
        migrations.CreateModel(
            name='ShortNotice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime(2022, 7, 2, 1, 1, 2, 712315, tzinfo=utc))),
                ('sn_status', models.CharField(choices=[('1', 'Add'), ('2', 'Cancel'), ('3', 'Move')], default='1', max_length=1)),
                ('adopter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adopter.adopter')),
                ('current_appt', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prev_appt', to='appt_calendar.appointment')),
                ('prev_appt', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_appt', to='appt_calendar.appointment')),
            ],
        ),
    ]
