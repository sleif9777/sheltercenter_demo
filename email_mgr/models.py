from django.db import models
from tinymce.models import HTMLField

# Create your models here.
class EmailTemplate(models.Model):

    template_name = models.CharField(default="", max_length=200, blank=True) #need to refactor and add verbose
    description = models.CharField(default="", max_length=500, blank=True)
    text = models.TextField(blank=True, null=True)

    def __repr__(self):
        return self.template_name

    def __str__(self):
        return self.template_name

    class Meta:
        ordering = ('template_name',)

class PendingMessage(models.Model):
    subject = models.CharField(default="", max_length=300)
    text = models.TextField(default="", blank=True)
    html = models.TextField(default="", blank=True)
    email = models.EmailField(default="")

    def __repr__(self):
        return "{0} [{1}]".format(self.subject, self.email)

    def __str__(self):
        return "{0} [{1}]".format(self.subject, self.email)

    class Meta:
        ordering = ('id',)
