from django.contrib import admin
from .models import TimeslotTemplate, Daily_Schedule, AppointmentTemplate, SystemSettings

admin.site.register(TimeslotTemplate)
admin.site.register(Daily_Schedule)
admin.site.register(AppointmentTemplate)
admin.site.register(SystemSettings)
