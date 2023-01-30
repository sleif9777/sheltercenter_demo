import datetime

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from appt_calendar.date_time_strings import *

# Create your models here.
class Organization(models.Model):
    auth_code = models.IntegerField(
        default=100000, validators=[
            MinValueValidator(100000), MaxValueValidator(999999)
        ]
    )
    contact_email = models.EmailField(default="", blank=True)
    has_event = models.BooleanField(default=False)
    leader_fname = models.CharField(default="", max_length=20, blank=True)
    leader_lname = models.CharField(default="", max_length=20, blank=True)
    org_name = models.CharField(default="", max_length=100, blank=True)
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

    def __repr__(self):
        return self.org_name

    def __str__(self):
        return self.org_name

    def leader_name(self):
        return "{0} {1}".format(
            self.leader_fname, self.leader_lname)

    def leader_name_upper(self):
        return "{0} {1}".format(
            self.leader_fname, self.leader_lname).upper()


class VolunteeringEvent(models.Model):
    #basic info
    available = models.BooleanField(default=True)
    date = models.DateField(default=datetime.date(2000,1,1))
    event_counselor = models.CharField(default="", max_length=30, blank=True)
    event_end_time = models.TimeField(default=datetime.time(9,0))
    event_start_time = models.TimeField(default=datetime.time(9,0))
    event_task = models.CharField(default="", max_length=200, blank=True)
    organization = models.ForeignKey(
        Organization, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    volunteer_maximum = models.IntegerField(default=0, blank=True)
    volunteer_minimum = models.IntegerField(default=0, blank=True)

    #statuses
    donation_received = models.BooleanField(default=False)
    marked_as_complete = models.BooleanField(default=False)
    posted_social_media = models.BooleanField(default=False)
    sent_thank_you = models.BooleanField(default=False)
    waivers_complete = models.BooleanField(default=False)

    def __repr__(self):
        try:
            return self.organization.org_name.upper()
        except:
            return self.date_string()

    def __str__(self):
        try:
            return self.organization.org_name.upper()
        except:
            return self.date_string()

    def date_string(self):
        return date_no_weekday_str(self.date)

    def start_and_end(self):
        start_time_str = time_str(self.event_start_time)
        end_time_str = time_str(self.event_end_time)
        return "({0} - {1})".format(start_time_str, end_time_str)

    def volunteer_count_str(self):
        min = self.volunteer_minimum
        max = self.volunteer_maximum

        if min == max:
            return str(max)
        else:
            return "{0} to {1}".format(min, max)

    def delist(self):
        self.organization.has_event = True
        self.organization.save()
        
        self.available = False
        self.save()

    def relist(self, organization):
        organization.has_event = False
        organization.save()

        self.organization = None
        self.available = True
        self.save()
