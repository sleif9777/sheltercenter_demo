from django.db import models
# from io import StringIO
# from html.parser import HTMLParser
#
# class MLStripper(HTMLParser):
#     def __init__(self):
#         super().__init__()
#         self.reset()
#         self.strict = False
#         self.convert_charrefs= True
#         self.text = StringIO()
#     def handle_data(self, d):
#         self.text.write(d)
#     def get_data(self):
#         return self.text.getvalue()

# Create your models here.

class FAQ(models.Model):
    question = models.CharField(default="", max_length=500)
    answer = models.TextField(default="", blank=False)
    order = models.IntegerField(default=1)

    def __repr__(self):
        return self.question

    def __str__(self):
        return self.question

    class Meta:
        ordering = ('order', 'question')

class FAQSection(models.Model):
    name = models.CharField(default="", max_length=200)
    questions = models.ManyToManyField(FAQ, blank=True)
    order = models.IntegerField(default=1)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id', 'order', 'name')

class HelpTopic(models.Model):
    header = models.CharField(default="", max_length=500)
    text = models.TextField(default="", blank=False)
    order = models.IntegerField(default=1)

    def __repr__(self):
        return self.header

    def __str__(self):
        return self.header

    class Meta:
        ordering = ('order', 'header')

class HelpSection(models.Model):
    name = models.CharField(default="", max_length=200)
    topics = models.ManyToManyField(HelpTopic, blank=True)
    order = models.IntegerField(default=1)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id', 'order', 'name')

class VisitorInstruction(models.Model):
    header = models.CharField(default="", max_length=500)
    text = models.TextField(default="", blank=False)
    order = models.IntegerField(default=1)

    def __repr__(self):
        return self.header

    def __str__(self):
        return self.header

    class Meta:
        ordering = ('order', 'id', 'header')
