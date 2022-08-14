import datetime

from django.db import models

class Dog(models.Model):
    name = models.CharField(default = "", max_length = 200)
    shelterluv_id = models.CharField(default = "", max_length = 200)
    shelterluv_status = models.CharField(default = "Available for Adoption", max_length = 200)
    info = models.JSONField()
    offsite = models.BooleanField(default=False)
    appt_only = models.BooleanField(default=False)
    # host_date = models.DateField(default=datetime.date(2000,1,1), blank=True)
    # foster_date = models.DateField(default=datetime.date(2000,1,1), blank=True)

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
