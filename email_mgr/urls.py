from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.email_home, name="email_home"),
    path("add/", views.add_email_template, name="add_email_template"),
]
