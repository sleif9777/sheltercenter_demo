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
from django.urls import include, path
from django.conf.urls.static import static

import adopter, visit_and_faq
from . import settings
from adopter import views
from appt_calendar import views
from dashboard import views as views

urlpatterns = [
    path('', views.login_page, name="home_page"),
    path('admin/', admin.site.urls),
    path('calendar/template/', include('schedule_template.urls')),
    path('calendar/', include('appt_calendar.urls')),
    path('adopter/', include('adopter.urls')),
    path('emails/', include('email_mgr.urls')),
    path('visit_comms/', include('visit_and_faq.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('login/', views.login_page, name="login"),
    path('settings/', views.user_settings, name='user_settings'),
    path('logout/', views.logout_user, name="logout"),
    path('login/staff/', views.staff_login, name="staff_login"),
    path('images/', views.images, name="images"),
    path('help/', visit_and_faq.views.help, name="help"),
    path('fake500/', views.fake500, name="fake500"),
    path('tinymce/', include('tinymce.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)

handler500 = 'dashboard.views.error_500'
