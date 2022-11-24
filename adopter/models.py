import datetime

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from num2words import num2words

from wishlist.models import Dog

class Adopter(models.Model):
    STATUSES = [
        ("1", "Approved"),
        ("2", "Blocked"),
        ("3", "Pending")
    ]

    PREF_GENDERS = [
        ("1", "No Preference"),
        ("2", "Female Only"),
        ("3", "Male Only"),
    ]

    PREF_AGES = [
        ("1", "No Preference"),
        ("2", "Puppies Only"),
        ("3", "Adults Only")
    ]

    #personal attributes
    f_name = models.CharField(default="", max_length=200, blank=True) #need to refactor and add verbose
    l_name = models.CharField(default="", max_length=200, blank=True) #""
    primary_email = models.EmailField(default="", blank=True) #""
    secondary_email = models.EmailField(default="", blank=True)
    city = models.CharField(default="", max_length=200, blank=True)
    state = models.CharField(default="", max_length=2, blank=True)
    phone_number = models.CharField(default="See application", max_length=20, blank=True)

    #application attributes
    application_id = models.CharField(default="", max_length=20, blank=True)
    accept_date = models.DateField(default=datetime.date.today(), blank=True)
    housing_type = models.CharField(default="", max_length=200, blank=True)
    housing = models.CharField(default="", max_length=200, blank=True)
    activity_level = models.CharField(default="", max_length=200, blank=True)
    has_fence = models.BooleanField(default=False, blank=True)
    app_interest = models.CharField(default="", max_length=2000, blank=True)
    wishlist = models.ManyToManyField(Dog, null=True, blank=True)

    #adoption-related attributes
    out_of_state = models.BooleanField(default = False)
    lives_with_parents = models.BooleanField(default = False)
    adopting_host = models.BooleanField(default = False)
    adopting_foster = models.BooleanField(default = False)
    friend_of_foster = models.BooleanField(default = False)
    carryover_shelterluv = models.BooleanField(default = False)
    chosen_dog = models.CharField(default="", max_length=200, blank=True)
    waiting_for_chosen = models.BooleanField(default=False)

    #preference attributes
    min_weight = models.IntegerField(default = 0,)
    max_weight = models.IntegerField(default = 0,)
    hypo_preferred = models.BooleanField(default = False)
    gender_preference = models.CharField(default="1", max_length=1, choices=PREF_GENDERS)
    age_preference = models.CharField(default="1", max_length=1, choices=PREF_AGES)

    #database-related attributes
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    auth_code = models.IntegerField(default = 100000, validators = [MinValueValidator(100000), MaxValueValidator(999999)])
    acknowledged_faq = models.BooleanField(default = False)
    has_current_appt = models.BooleanField(default = False)
    alert_date = models.DateField(default=datetime.date(datetime.date.today().year,1,1), blank=True)
    visits_to_date = models.IntegerField(default=0)
    adoption_complete = models.BooleanField(default=False)
    requested_access = models.BooleanField(default=False)
    requested_surrender = models.BooleanField(default=False)
    status = models.CharField(default="1", max_length=1, choices=STATUSES)

    def number_of_visits(self):
        ordinal = num2words(self.visits_to_date + 1, to='ordinal')

        #if an adopter has come for 1 visit and visits_to_date == 1, then the string should be "second visit" as that is what is upcoming

        ordinal = ordinal[0].upper() + ordinal[1:]
        ordinal = ordinal + " visit"

        if self.visits_to_date >= 2:
            for i in range(2, self.visits_to_date + 1):
                ordinal += "!"

        return ordinal

    def full_name(self):
        return self.f_name + " " + self.l_name

    def adopter_list_name(self):
        return self.l_name + ", " + self.f_name

    def app_interest_str(self):
        if len(self.app_interest) > 50:
            return self.app_interest[:48] + "..."
        else:
            return self.app_interest

    def chg_appt_status(self):
        self.has_current_appt = not self.has_current_appt
        self.save()

    def __repr__(self):
        return self.full_name()

    def __str__(self):
        return self.full_name()

    def show_preferences(self):
        if self.min_weight != 0:
            return True
        if self.max_weight != 0:
            return True
        if self.hypo_preferred:
            return True
        if self.gender_preference != "1":
            return True
        if self.age_preference != "1":
            return True

        return False

    class Meta:
        ordering = ('f_name', 'l_name')
