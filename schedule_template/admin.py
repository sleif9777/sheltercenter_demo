from django.contrib import admin

from .models import AppointmentTemplate, Daily_Schedule, TimeslotTemplate, SystemSettings

admin.site.register(TimeslotTemplate)
admin.site.register(Daily_Schedule)
admin.site.register(AppointmentTemplate)
admin.site.register(SystemSettings)
