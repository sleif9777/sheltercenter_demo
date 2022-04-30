from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(HelpTopic)
admin.site.register(HelpSection)
admin.site.register(FAQ)
admin.site.register(FAQSection)
admin.site.register(VisitorInstruction)
