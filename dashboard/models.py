from email.policy import default
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    first_name = models.CharField(default="", max_length=200)
    last_name = models.CharField(default="", max_length=200)
    signature = models.TextField(default="")
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

    #appointment card attributes
    ac_show_booking_timestamp = models.BooleanField(default=True)

    def __repr__(self):
        return self.user.username

    def __str__(self):
        return self.user.username

    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)
