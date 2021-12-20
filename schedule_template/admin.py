from django.contrib import admin
from .models import TimeslotTemplate, Daily_Schedule, AppointmentTemplate

admin.site.register(TimeslotTemplate)
admin.site.register(Daily_Schedule)
admin.site.register(AppointmentTemplate)
