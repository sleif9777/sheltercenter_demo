from django.contrib import admin

from .models import *

admin.site.register(EmailTemplate)
admin.site.register(PendingMessage)
