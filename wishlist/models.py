from django.db import models

class Dog(models.Model):
    shelterluv_id = models.CharField(default = "", max_length = 200)
    info = models.JSONField()

    def __repr__(self):
        return self.info['Name']

    def __str__(self):
        return self.info['Name']
