from django.db import models
from django.utils import timezone
import datetime
from .date_time_strings import *
from adopter.models import Adopter
from num2words import num2words
from copy import copy

class DailyAnnouncement(models.Model):
    date = models.DateField(default = timezone.now())
    text = models.TextField(default="", blank=True)

class CalendarAnnouncement(models.Model):
    text = models.TextField(default="", blank=True)

class Appointment(models.Model):
    APPT_TYPES = [
        ("1", "Adults"),
        ("2", "Puppies"),
        ("3", "Puppies or Adults"),
        ("4", "Surrender"),
        ("5", "Adoption Paperwork"),
        ("6", "FTA Paperwork"),
        ("7", "Visit")
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
        ("10", "Chosen - needs well check")
    ]

    #appt basic information
    date = models.DateField(default = timezone.now())
    time = models.TimeField(default=datetime.time(12,00))
    appt_type = models.CharField(default="1", max_length=1, choices=APPT_TYPES)

    #booking information
    adopter = models.ForeignKey(Adopter, null=True, blank=True, on_delete=models.SET_NULL)
    available = models.BooleanField(default = True) #is not filled
    published = models.BooleanField(default = True) #can be seen by public
    locked = models.BooleanField(default = False) #when published = True, if locked, public can see but not interact

    #adopter note attributes
    internal_notes = models.TextField(default="", blank=True)
    adopter_notes = models.TextField(default="", blank=True)

    #communication attributes
    comm_adopted_dogs = models.BooleanField(default=False)
    comm_limited_puppies = models.BooleanField(default=False)
    comm_limited_small = models.BooleanField(default=False)
    comm_limited_hypo = models.BooleanField(default=False)
    comm_limited_other = models.BooleanField(default=False)
    comm_limited_small_puppies = models.BooleanField(default=False)
    comm_followup = models.BooleanField(default=False)

    #adopter attributes
    visits_to_date = models.IntegerField(default=0)
    bringing_dog = models.BooleanField(default=False)
    has_cat = models.BooleanField(default=False)
    mobility = models.BooleanField(default=False)

    #post-visit attributes
    outcome = models.CharField(default="1", max_length = 2, choices=OUTCOME_TYPES)
    dog = models.CharField(default="", max_length=200, blank=True) #this can also be used in surrenders
    dog_fka = models.CharField(default="", max_length=200, blank=True) #only used for surrenders
    heartworm = models.BooleanField(default=False)
    last_update_sent = models.DateField(default=timezone.now(), blank=True)
    paperwork_complete = models.BooleanField(default=False)

    def __repr__(self):
        display_string = ""
        render_appt_type = self.appt_string()

        if int(self.appt_type) <= 3:
            if self.adopter is not None:
                display_string += str(self.adopter).upper()
            else:
                display_string += "OPEN"

        elif int(self.appt_type) > 3:
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
        elif int(self.appt_type) > 3:
            if self.dog == "":
                display_string += "OPEN"
            else:
                display_string += self.dog.upper()

                if self.dog_fka != "":
                    display_string += " fka " + self.dog_fka.upper()

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

    def appt_string(self):
        appt_type = ["Adults", "Puppies", "Puppies or Adults", "Surrender", "Adoption", "FTA", "Visit"]
        return appt_type[int(self.appt_type) - 1]

    def reset(self):
        # clears all information out of an appointment and republishes it for booking

        self.adopter = None
        self.available = True
        self.published = True

        self.internal_notes = ""
        self.adopter_notes = ""

        self.comm_adopted_dogs = False
        self.comm_limited_puppies = False
        self.comm_limited_small = False
        self.comm_limited_hypo = False
        self.comm_limited_other = False
        self.comm_limited_small_puppies = False

        self.visits_to_date = 0
        self.bringing_dog = False
        self.has_cat = False
        self.mobility = False

        self.outcome = "1"
        self.dog = ""
        self.dog_fka = ""
        self.paperwork_complete = False
        self.save()

    def delist(self):
        # sets the adopter upon booking and changes their appt status,
        # turns off the publish and available attributes of an appt

        self.available = False
        self.published = False

        if self.adopter is not None:
            self.visits_to_date = copy(self.adopter.visits_to_date)

            if self.adopter.acknowledged_faq == False:
                self.adopter.acknowledged_faq = True
                self.adopter.save()

        self.save()

    class Meta:
        ordering = ('time', 'appt_type', 'id',)

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
