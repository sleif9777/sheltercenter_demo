from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    first_name = models.CharField(default="", max_length=200)
    last_name = models.CharField(default="", max_length=200)
    signature = models.TextField(default="")
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

    def __repr__(self):
        return self.user.username

    def __str__(self):
        return self.user.username
