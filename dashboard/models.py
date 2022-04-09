from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class AdminProfile(models.Model):
    first_name = models.CharField(default="", max_length=200)
    last_name = models.CharField(default="", max_length=200)
    signature = models.CharField(default="", max_length=200)
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
