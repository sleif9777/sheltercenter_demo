"""sheltercenter_schedule URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from appt_calendar import views as cal_views
from adopter import views as adopt_views
#import scheduleconfig.views
#import schedule_template.views
#import appt_calendar.views
#import adopter_mgmt.views


urlpatterns = [
    path('admin/', admin.site.urls),
    #path("", views.home, name='home'),
    #path("schedule/", views.schedule, name='schedule'),
    #path("scheduletest/", views.scheduletest, name='scheduletest'),
    #path("config/createtimeslot/", scheduleconfig.views.createtimeslot, name="createtimeslot"),
    path('calendar/template/', include('schedule_template.urls')),
    path('calendar/', include('appt_calendar.urls')),
    path('adopter/', include('adopter.urls')),
    path('', adopt_views.simple_add_form, name="home")
]
