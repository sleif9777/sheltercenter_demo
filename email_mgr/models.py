from django.db import models
from tinymce.models import HTMLField

# Create your models here.
class EmailTemplate(models.Model):

    template_name = models.CharField(default="", max_length=200, blank=True) #need to refactor and add verbose
    text = models.TextField(blank=True, null=True)

    def __repr__(self):
        return self.template_name

    def __str__(self):
        return self.template_name

    class Meta:
        ordering = ('template_name',)
