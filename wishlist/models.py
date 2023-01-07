import datetime

from django.db import models

# DEPRECATED, DO NOT USE
class Dog(models.Model):
    shelterluv_id = models.CharField(default="", max_length = 200)
    name = models.CharField(default="", null=True, max_length=20)
    shelterluv_status = models.CharField(default="Available for Adoption", max_length=200)
    info = models.JSONField()

    def __repr__(self):
        return self.info['Name']

    def __str__(self):
        return self.info['Name']

    def Age_str(self):
        age = int(self.info['Age'])

        return "Age {0}Y {1}M".format(age // 12, age % 12)

    def Weight_str(self):
        try:
            weight = int(self.info['CurrentWeightPounds'])
            return "{0} lbs., ".format(weight)
        except:
            return ""


# class Litter(models.Model):
#     name = models.CharField(default="")
#     any_available = models.BooleanField(default=False)

# TO DO:
# add dogs as many to many
# method for check if any available any([dog.available() for dog in self.dogs.iterator()])
# get or create when pulling in dogs using dog.litter_id
# functionality - show a manage litters page tracking litter adoptions and allowing batch email sendouts
# add same batch email to manage dogs
    


# USE THIS INSTEAD
class DogProfile(models.Model):
    name = models.CharField(default="", max_length=200)
    shelterluv_id = models.CharField(default = "", max_length = 200)
    shelterluv_status = models.CharField(default = "Available for Adoption", max_length = 200)
    info = models.JSONField()
    offsite = models.BooleanField(default=False)
    appt_only = models.BooleanField(default=False)
    host_date = models.DateField(default=datetime.date(2000,1,1), blank=True)
    foster_date = models.DateField(default=datetime.date(2000,1,1), blank=True)
    litter_id = models.CharField(default=None, max_length=20, null=True)
    update_dt = models.DateTimeField(default=datetime.datetime(2000,1,1,0,0), blank=True)

    def __repr__(self):
        return self.info['Name']

    def __str__(self):
        return self.info['Name']

    def Age_str(self):
        age = int(self.info['Age'])
        return "Age {0}Y {1}M".format(age // 12, age % 12)

    def Weight_str(self):
        try:
            weight = int(self.info['CurrentWeightPounds'])
            return "{0} lbs., ".format(weight)
        except:
            return ""

    def available(self):
        return self.shelterluv_status == "Available for Adoption"

    def host_date_str(self):
        if self.host_date.year != 2000:
            return self.host_date.strftime("%Y-%m-%d")
        else:
            return

    def foster_date_str(self):
        if self.foster_date.year != 2000:
            return self.foster_date.strftime("%Y-%m-%d")
        else:
            return


    class Meta:
        ordering = ('name', 'id',)