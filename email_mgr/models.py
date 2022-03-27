from django.db import models
from tinymce.models import HTMLField
from ckeditor.fields import RichTextField

# Create your models here.
class EmailTemplate(models.Model):

    template_name = models.CharField(default="", max_length=200, blank=True) #need to refactor and add verbose
    text = models.TextField(blank=True, null=True)
    plain = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('template_name',)

class EmailTemplate2(models.Model):

    template_name = models.CharField(default="", max_length=200, blank=True) #need to refactor and add verbose
    text = HTMLField(blank=True)
