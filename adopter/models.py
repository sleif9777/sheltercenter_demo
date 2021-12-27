from django.db import models
import datetime

# Create your models here.

class Adopter(models.Model):
    adopter_first_name = models.CharField(default="", max_length=200, blank=True)
    adopter_last_name = models.CharField(default="", max_length=200, blank=True)
    adopter_email = models.EmailField(default="", blank=True)
    acknowledged_faq = models.BooleanField(default = False)
    out_of_state = models.BooleanField(default = False)
    lives_with_parents = models.BooleanField(default = False)
    adopting_host = models.BooleanField(default = False)
    adopting_foster = models.BooleanField(default = False)
    friend_of_foster = models.BooleanField(default = False)
    chosen_dog = models.CharField(default="", max_length=200, blank=True)
    has_current_appt = models.BooleanField(default = False)
    alert_date = models.DateField(default=datetime.date(2000,1,1), blank=True)

    def adopter_full_name(self):
        return self.adopter_first_name + " " + self.adopter_last_name

    def adopter_list_name(self):
        return self.adopter_last_name + ", " + self.adopter_first_name

    def adopter_email_prefix(self):
        split_email = self.adopter_email.split("@")

        return split_email[0]

    def __repr__(self):
        return self.adopter_full_name()

    def __str__(self):
        return self.adopter_full_name()

    class Meta:
        ordering = ('adopter_last_name', 'adopter_first_name')
