import datetime

from django.db import models

from appt_calendar.date_time_strings import *

# Create your models here.

class SystemSettings(models.Model):
    last_adopter_upload = models.DateField(default=datetime.date.today())

class AppointmentTemplate(models.Model):
    APPT_TYPES = [
        ("1", "Adults"),
        ("2", "Puppies"),
        ("3", "Puppies and/or Adults"),
        ("4", "Surrender"),
        ("5", "Adoption"),
        ("6", "FTA"),
        ("7", "Visit"),
        ("8", "Donation Drop-Off"),
        ("9", "Host Weekend/Chosen")
    ]

    DAYS_OF_WEEK = (
        ("6", "Sunday"),
        ("0", "Monday"),
        ("1", "Tuesday"),
        ("2", "Wednesday"),
        ("3", "Thursday"),
        ("4", "Friday"),
        ("5", "Saturday"),
    )

    day_of_week = models.CharField(default="0", max_length=1, choices=DAYS_OF_WEEK)
    time = models.TimeField(default=datetime.time(12,00))
    appt_type = models.CharField(default="1", max_length=1, choices=APPT_TYPES)

    def __repr__(self):
        render_dow = self.dow_string()
        render_time = self.time_string()
        render_appt_type = self.appt_string()

        return render_dow + "s at " + render_time

    def __str__(self):
        render_dow = self.dow_string()
        render_time = self.time_string()
        render_appt_type = self.appt_string()

        return render_dow + "s at " + render_time

    def dow_string(self):
        dows = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return dows[int(self.day_of_week)]

    def time_string(self):
        return time_str(self.time)

    def appt_string(self):
        appt_type = ["Adults", "Puppies", "Puppies and/or Adults", "Surrender", "Adoption", "FTA", "Visit", "Donation Drop-Off", "Host Weekend/Chosen"]
        return appt_type[int(self.appt_type) - 1]

    class Meta:
        ordering = ('time', 'appt_type',)

class TimeslotTemplate(models.Model):
    DAYS_OF_WEEK = (
        ("6", "Sunday"),
        ("0", "Monday"),
        ("1", "Tuesday"),
        ("2", "Wednesday"),
        ("3", "Thursday"),
        ("4", "Friday"),
        ("5", "Saturday"),
    )

    day_of_week = models.CharField(default="0", max_length=1, choices=DAYS_OF_WEEK)
    time = models.TimeField(default=datetime.time(12,00))
    appointments = models.ManyToManyField(AppointmentTemplate, blank=True)

    def __str__(self):
        render_time = self.time_string()
        return render_time

    def time_string(self):
        return time_str(self.time)

    class Meta:
        ordering = ('time',)


class Daily_Schedule(models.Model):

    DAYS_OF_WEEK = (
        ("6", "Sunday"),
        ("0", "Monday"),
        ("1", "Tuesday"),
        ("2", "Wednesday"),
        ("3", "Thursday"),
        ("4", "Friday"),
        ("5", "Saturday"),
    )

    day_of_week = models.CharField(default="0", max_length=1, choices=DAYS_OF_WEEK)
    timeslots = models.ManyToManyField(TimeslotTemplate, blank=True)

    def __str__(self):
        render_dow = self.dow_string()
        return render_dow

    def dow_string(self):
        dows = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return dows[int(self.day_of_week)]
