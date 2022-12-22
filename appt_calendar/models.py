import datetime

from copy import copy
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from num2words import num2words

from .date_time_strings import *
from adopter.models import Adopter

class DailyAnnouncement(models.Model):
    date = models.DateField(default = timezone.now())
    text = models.TextField(default="", blank=True)

class InternalAnnouncement(models.Model):
    date = models.DateField(default = timezone.now())
    text = models.TextField(default="", blank=True)

class CalendarAnnouncement(models.Model):
    text = models.TextField(default="", blank=True)

class Appointment(models.Model):
    APPT_TYPES = [
        ("1", "Adults"),
        ("2", "Puppies"),
        ("3", "Puppies and/or Adults"),
        ("4", "Surrender"),
        ("5", "Adoption Paperwork"),
        ("6", "FTA Paperwork"),
        ("7", "Visit"),
        ("8", "Donation Drop-Off")
    ]

    OUTCOME_TYPES = [
        ("1", "NA"),
        ("2", "Adoption"),
        ("3", "Chosen"),
        ("4", "FTA"),
        ("5", "No Decision"),
        ("6", "No Show"),
        ("7", "Ready To Roll"),
        ("8", "Paperwork Scheduled"),
        ("9", "Chosen - needs vetting"),
        ("10", "Chosen - needs well check"),
        ("11", "Error")
    ]

    #appt basic information
    appt_type = models.CharField(default="1", max_length=1, choices=APPT_TYPES)
    date = models.DateField(default=timezone.now())
    short_notice = models.BooleanField(default=False)
    time = models.TimeField(default=datetime.time(12,00))

    #check-in information
    adopter_description = models.CharField(default="", max_length=50, blank=True)
    checked_in = models.BooleanField(default=False)
    checked_in_time = models.TimeField(default=datetime.time(00,00))
    checked_out_time = models.TimeField(default=datetime.time(00,00))
    counselor = models.CharField(default="", max_length=20, blank=True)

    #booking information
    adopter = models.ForeignKey(Adopter, null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'has_current_appt': False, 'status': "1"})
    available = models.BooleanField(default=True) #is not filled
    dt_booking = models.DateTimeField(default=datetime.datetime(2000,1,1,0,0), blank=True)
    locked = models.BooleanField(default=False) #when published = True, if locked, public can see but not interact
    published = models.BooleanField(default=True) #can be seen by public

    #adopter note attributes
    internal_notes = models.TextField(default="", blank=True)
    adopter_notes = models.TextField(default="", blank=True, max_length="50")

    #communication attributes
    comm_adopted_dogs = models.BooleanField(default=False)
    comm_dog_in_extended_host = models.BooleanField(default=False)
    comm_dog_in_medical_foster = models.BooleanField(default=False)
    comm_dog_is_popular = models.BooleanField(default=False)
    comm_dog_is_popular_low_chances = models.BooleanField(default=False)
    comm_dog_not_here_yet = models.BooleanField(default=False)
    comm_followup = models.BooleanField(default=False)
    comm_limited_hypo = models.BooleanField(default=False)
    comm_limited_other = models.BooleanField(default=False)
    comm_limited_puppies = models.BooleanField(default=False)
    comm_limited_small = models.BooleanField(default=False)
    comm_limited_small_puppies = models.BooleanField(default=False)
    comm_reminder_breed = models.BooleanField(default=False)
    comm_reminder_parents = models.BooleanField(default=False)

    #adopter attributes
    bringing_dog = models.BooleanField(default=False)
    has_cat = models.BooleanField(default=False)
    mobility = models.BooleanField(default=False)
    visits_to_date = models.IntegerField(default=0)

    #post-visit attributes
    all_updates_sent = ArrayField(
        models.CharField(max_length=30, blank=True), default=[]
    )
    dog = models.CharField(default="", max_length=200, blank=True) #this can also be used in surrenders
    dog_fka = models.CharField(default="", max_length=200, blank=True) #only used for surrenders
    heartworm = models.BooleanField(default=False)
    last_update_sent = models.DateField(default=timezone.now(), blank=True)
    outcome = models.CharField(default="1", max_length=2, choices=OUTCOME_TYPES)
    paperwork_complete = models.BooleanField(default=False)
    rtr_notif_date = models.CharField(default="", max_length=200, blank=True)

    def __repr__(self):
        display_string = ""
        render_appt_type = self.appt_string()

        if int(self.appt_type) <= 3:
            if self.adopter is not None:
                display_string += str(self.adopter).upper()
            else:
                display_string += "OPEN"

        elif int(self.appt_type) in range(3, 8): #exclude drop-off appts
            if self.dog == "":
                display_string += "MORE DETAILS NEEDED"
            else:
                display_string += self.dog.upper()

                if self.dog_fka != "":
                    display_string += " fka " + self.dog_fka.upper()

        return display_string

    def __str__(self):
        display_string = ""
        render_appt_type = self.appt_string()

        if int(self.appt_type) <= 3:
            if self.adopter is not None:
                display_string += str(self.adopter).upper()
            else:
                display_string += "OPEN"

        elif int(self.appt_type) in range(3, 8): #exclude drop-off appts
            if self.dog == "":
                display_string += "MORE DETAILS NEEDED"
            else:
                display_string += self.dog.upper()

                if self.dog_fka != "":
                    display_string += " fka " + self.dog_fka.upper()

        else:
            display_string = "DONATION DROP-OFF"

        return display_string

    def number_of_visits(self):
        ordinal = num2words(self.visits_to_date + 1, to='ordinal')

        #if an adopter has come for 1 visit and visits_to_date == 1, then the string should be "second visit" as that is what is upcoming

        ordinal = ordinal[0].upper() + ordinal[1:]
        ordinal = ordinal + " visit"

        if self.visits_to_date >= 2:
            for i in range(2, self.visits_to_date + 1):
                ordinal += "!"

        return ordinal

    def date_string(self):
        return date_str(self.date)

    def time_string(self):
        return time_str(self.time)

    def date_and_time_string(self):
        return self.date_string() + " at " + self.time_string()

    def dt_booking_string(self):
        return "Booked {0} at {1}".format(date_num_str(self.dt_booking), time_str(self.dt_booking))

    def appt_string(self):
        appt_type = ["Adults", "Puppies", "Puppies and/or Adults", "Surrender", "Adoption", "FTA", "Visit", "Donation Drop-Off"]
        return appt_type[int(self.appt_type) - 1]

    def mark_short_notice(self):
        self.short_notice = True
        self.save()

    def reset(self):
        # clears all information out of an appointment and republishes it for booking

        self.adopter = None
        self.available = True
        self.dt_booking = datetime.datetime(2000,1,1,0,0)
        self.published = True
        self.short_notice = False

        self.adopter_notes = ""
        self.internal_notes = ""

        self.comm_adopted_dogs = False
        self.comm_limited_hypo = False
        self.comm_limited_other = False
        self.comm_limited_puppies = False
        self.comm_limited_small = False
        self.comm_limited_small_puppies = False

        self.bringing_dog = False
        self.has_cat = False
        self.mobility = False
        self.visits_to_date = 0

        self.dog = ""
        self.dog_fka = ""
        self.outcome = "1"
        self.paperwork_complete = False
        self.save()

    def delist(self):
        # sets the adopter upon booking and changes their appt status,
        # turns off the publish and available attributes of an appt

        self.available = False
        self.published = False

        if self.adopter is not None:
            self.dt_booking = timezone.localtime(timezone.now()) #datetime.datetime.now()
            self.visits_to_date = copy(self.adopter.visits_to_date)

            if self.adopter.acknowledged_faq == False:
                self.adopter.acknowledged_faq = True
                self.adopter.save()

        self.save()

    class Meta:
        ordering = ('time', 'adopter', 'appt_type', 'id',)

class Timeslot(models.Model):
    date = models.DateField(default = timezone.now())
    time = models.TimeField(default=datetime.time(12,00))
    appointments = models.ManyToManyField(Appointment, blank=True)

    def __str__(self):
        render_time = self.time_string()
        return render_time

    def time_string(self):
        return time_str(self.time)

    class Meta:
        ordering = ('time',)

class ShortNotice(models.Model):
    STATUS_TYPES = [
        ("1", "Add"),
        ("2", "Cancel"),
        ("3", "Move"),
    ]

    adopter = models.ForeignKey(Adopter, null=True, blank=True, on_delete=models.SET_NULL)
    dog = models.CharField(default="", max_length=200, blank=True) #this can also be used in surrenders
    current_appt = models.ForeignKey(Appointment, null=True, blank=True, on_delete=models.SET_NULL, related_name="prev_appt")
    date = models.DateField(default = timezone.now())
    prev_appt = models.ForeignKey(Appointment, null=True, blank=True, on_delete=models.SET_NULL, related_name="current_appt")
    backup_str = models.CharField(default="", max_length=100, blank=True)
    header_str = models.CharField(default="", max_length=100, blank=True)
    sn_status = models.CharField(default="1", max_length=1, choices=STATUS_TYPES)

    def set_backup(self):
        self.header_str = str(self)

        if self.sn_status == "1":
            self.backup_str = "{0} - {1}".format(self.current_appt.appt_string(), self.current_appt.time_string())
        if self.sn_status == "2":
            self.backup_str = "{0} - {1}".format(self.prev_appt.appt_string(), self.prev_appt.time_string())
        if self.sn_status == "3":
            self.backup_str = "{0} - moved from {1} to {2}".format(self.current_appt.appt_string(), self.prev_appt.time_string(), self.current_appt.time_string())
        self.save()

    def __repr__(self):
        schedulable = False

        try:
            if self.current_appt.appt_type in ["1", "2", "3"]:
                schedulable = True
                appt = self.current_appt
        except:
            try:
                if self.prev_appt.appt_type in ["1", "2", "3"]:
                    schedulable = True
                    appt = self.prev_appt
            except:
                appt = "Deleted Appointment"

        if schedulable:
            # return self.adopter.full_name()
            try:
                return "{0}: ({1})".format(self.sn_status, self.adopter.full_name(),)
            except:
                return "{0}: (Unknown)"
        else:
            # return self.dog()
            return "{0}: {1}".format(self.sn_status, self.dog,)

    def __str__(self):
        schedulable = False

        try:
            if self.current_appt.appt_type in ["1", "2", "3"]:
                schedulable = True
        except Exception as uu:
            try:
                if self.prev_appt.appt_type in ["1", "2", "3"]:
                    schedulable = True
            except:
                pass

        if schedulable:
            try:
                return self.adopter.full_name()
            except:
                return "Unknown"
        else:
            try:
                return self.dog
            except:
                return "Unknown"
