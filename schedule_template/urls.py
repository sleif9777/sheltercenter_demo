from django.urls import path

from . import views
from appt_calendar import views as cal_views

urlpatterns = [
    path('<int:dow_id>/', views.daily, name='daily'),
    path("", views.weekly, name='weekly_schedule'),
    path('timeslot/add/<int:dow_id>/', views.add_timeslot, name="add_timeslot"),
    path('appt/add/<int:dow_id>/<int:timeslot_id>/', views.add_appointment, name="add_appointment"),
    path('appt/edit/<int:dow_id>/<int:appt_id>/', views.edit_appointment, name="edit_appointment"),
    path("timeslot/delete/<int:dow_id>/<int:timeslot_id>/", views.delete_timeslot, name="delete_timeslot"),
    path("appt/delete/<int:dow_id>/<int:appt_id>/", views.delete_appointment, name="delete_appointment"),
]
