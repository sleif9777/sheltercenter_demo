import datetime

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class CorporateVolunteeringEvent(models.Model):
    date = models.DateField(default=datetime.date(2000,1,1))
    org = models.OneToOneField(User, on_delete=models.CASCADE)


class CorporateVolunteeringOrganization(models.Model):
    org_name = models.CharField(default="", max_length=100, blank=True)
    leader_fname = models.CharField(default="", max_length=20, blank=True)
    leader_lname = models.CharField(default="", max_length=20, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    donation_interest = models.BooleanField(default=True)
