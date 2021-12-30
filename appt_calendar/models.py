from django.db import models
from django.utils import timezone
import datetime
from .date_time_strings import *
from adopter.models import Adopter

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
        ("6", "Ready To Roll"),
        ("7", "Paperwork Scheduled")
    ]

    # all_adopters = Adopter.objects
    #
    # print(all_adopters)
    #
    # ADOPTER_CHOICES = []
    #
    # for adopter in all_adopters.iterator():
    #     ADOPTER_CHOICES += [(str(adopter.id), adopter.adopter_full_name())]
    #
    # print(ADOPTER_CHOICES)

    #date = models.CharField(default=datetime.date.today)
    date = models.DateField(default = datetime.date.today())
    time = models.TimeField(default=datetime.time(12,00))
    appt_type = models.CharField(default="1", max_length=1, choices=APPT_TYPES)
    adopter_choice = models.ForeignKey(Adopter, null=True, blank=True, on_delete=models.SET_NULL)
    #adopter_choice = models.CharField(default="1", max_length=1, choices=ADOPTER_CHOICES)
    available = models.BooleanField(default = True) #is not filled
    published = models.BooleanField(default = True) #can be seen by public
    dog = models.CharField(default="", max_length=200, blank=True)
    dog_fka = models.CharField(default="", max_length=200, blank=True)
    internal_notes = models.TextField(default="", blank=True)
    adopter_notes = models.TextField(default="", blank=True)
    outcome = models.CharField(default="1", max_length = 1, choices=OUTCOME_TYPES)
    heartworm = models.BooleanField(default=False)
    bringing_dog = models.BooleanField(default=False)

    def __repr__(self):
        display_string = ""
        render_appt_type = self.appt_string()

        if int(self.appt_type) <= 3:
            if self.adopter_choice != None:
                display_string += str(self.adopter_choice).upper() + " (" + render_appt_type

                display_string += ")"
            else:
                display_string += "OPEN (" + render_appt_type + ")"
        elif int(self.appt_type) > 3:
            if self.dog == "":
                display_string += render_appt_type.upper() + " - MORE DETAILS NEEDED"
            else:
                display_string += self.dog.upper()

                if self.dog_fka != "":
                    display_string += " fka " + self.dog_fka.upper()

                display_string += " (" + render_appt_type + ")"

        return display_string

    def __str__(self):
        display_string = ""
        render_appt_type = self.appt_string()

        if int(self.appt_type) <= 3:
            if self.adopter_choice != None:
                display_string += str(self.adopter_choice).upper() + " (" + render_appt_type

                display_string += ")"
            else:
                display_string += "OPEN (" + render_appt_type + ")"
        elif int(self.appt_type) > 3:
            if self.dog == "":
                display_string += render_appt_type.upper() + " - MORE DETAILS NEEDED"
            else:
                display_string += self.dog.upper()

                if self.dog_fka != "":
                    display_string += " fka " + self.dog_fka.upper()

                display_string += " (" + render_appt_type + ")"

        return display_string

    def date_string(self):
        return date_str(self.date)

    def time_string(self):
        return time_str(self.time)

    def date_and_time_string(self):
        return self.date_string() + " at " + self.time_string()

    def appt_string(self):
        appt_type = ["Adults", "Puppies", "Puppies or Adults", "Surrender", "Adoption", "FTA", "Visit"]
        return appt_type[int(self.appt_type) - 1]

    class Meta:
        ordering = ('time', 'appt_type', 'id',)

class Timeslot(models.Model):
    date = models.DateField(default = datetime.date.today())
    time = models.TimeField(default=datetime.time(12,00))
    appointments = models.ManyToManyField(Appointment, blank=True)

    def __str__(self):
        render_time = self.time_string()
        return render_time

    def time_string(self):
        return time_str(self.time)

    class Meta:
        ordering = ('time',)
