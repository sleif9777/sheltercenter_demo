from django.contrib import admin

from .models import *

admin.site.register(Timeslot)
admin.site.register(Appointment)
admin.site.register(DailyAnnouncement)
admin.site.register(CalendarAnnouncement)
admin.site.register(ShortNotice)
