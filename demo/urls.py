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
from appt_calendar import views #as cal_views
from adopter import views #as adopt_views
from dashboard import views as dash_views
from . import settings
import adopter
from django.conf.urls.static import static

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
    path('emails/', include('email_mgr.urls')),
    path('', adopter.views.home_page, name="home_page"),
    path('register/', dash_views.register, name="register"),
    path('login/', dash_views.login_page, name="login"),
    path('logout/', dash_views.logout_user, name="logout"),
    path('test/', dash_views.test_harness, name="test_harness"),
    path('tinymce/', include('tinymce.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
