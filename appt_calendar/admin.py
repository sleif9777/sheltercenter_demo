from django.contrib import admin
from .models import Timeslot, Appointment, DailyAnnouncement

admin.site.register(Timeslot)
admin.site.register(Appointment)
admin.site.register(DailyAnnouncement)
