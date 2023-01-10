from django.urls import path

from . import views

urlpatterns = [
    path("", views.calendar, name="calendar"),
    path("manage_orgs/", views.manage_orgs, name="manage_orgs"),
]