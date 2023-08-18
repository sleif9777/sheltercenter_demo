from django.urls import path

from . import views
from appt_calendar import views as cal_views

urlpatterns = [
    path("", views.weekly, name='weekly_schedule'),
    path('edit?dow=<int:dow_id>/', views.daily, name='daily'),
    path('add?dow=<int:dow_id>/', views.add_timeslot, name="add_timeslot"),
    path('add?dow=<int:dow_id>?ts=<int:timeslot_id>/', views.add_appointment, name="add_appointment"),
    path('edit?dow=<int:dow_id>?appt=<int:appt_id>/', views.edit_appointment, name="edit_appointment"),
    path("delete?dow=<int:dow_id>?ts=<int:timeslot_id>/", views.delete_timeslot, name="delete_timeslot"),
    path("delete?dow=<int:dow_id>?appt=<int:appt_id>/", views.delete_appointment, name="delete_appointment"),
]
