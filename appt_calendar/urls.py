from django.urls import path
from . import views

urlpatterns = [
    #calendar view pages
    path("", views.calendar, name="calendar"),
    path("<int:date_year>/<int:date_month>/<int:date_day>/", views.calendar_date, name="calendar_date"),
    path("<int:date_year>/<int:date_month>/<int:date_day>/copy/", views.copy_temp_to_cal, name="copy_temp_to_cal"),
    path("<int:date_year>/<int:date_month>/<int:date_day>/print/", views.calendar_print, name="calendar_print"),
    path('schedule_next/adopter/<int:adopter_id>/appt/<int:appt_id>/jump_to_date/<str:source>/', views.jump_to_date_greeter, name="jump_to_date_greeter"),
    path("jump_to_date/", views.jump_to_date, name="jump_to_date"),

    #calendar admin pages
    path('edit_appt/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.edit_appointment, name="edit_cal_appointment"),
    path('edit_appt/mgmt/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.edit_appointment_from_mgmt, name="edit_cal_appointment_mgmt"),
    path('book_appt/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.book_appointment, name="book_cal_appointment"),
    path('delete_appt/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.delete_appointment, name="delete_cal_appointment"),
    path('add_appt/<int:timeslot_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.add_appointment, name="add_cal_appointment"),
    path('add_appt/followup/adopter/<int:adopter_id>/date/date/<int:date_year>/<int:date_month>/<int:date_day>/timeslot/<int:timeslot_id>/', views.add_followup_appointment, name="add_followup_appointment"),
    path('add_appt/paperwork/<int:timeslot_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/source/<int:originalappt_id>/', views.add_paperwork_appointment, name="add_paperwork_appointment"),
    path('announcement/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.add_daily_announcement, name="add_daily_announcement"),
    path('announcement/<int:announcement_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.edit_daily_announcement, name="edit_daily_announcement"),
    path('internal/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.add_internal_announcement, name="add_internal_announcement"),
    path('internal/<int:announcement_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.edit_internal_announcement, name="edit_internal_announcement"),
    path('calendar_note/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.add_calendar_announcement, name="add_calendar_announcement"),
    path('calendar_note/edit/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.edit_calendar_announcement, name="edit_calendar_announcement"),
    path('delete_timeslot/<int:timeslot_id>/<int:date_year>/<int:date_month>/<int:date_day>/', views.delete_timeslot, name="delete_cal_timeslot"),
    path('add_timeslot/<int:date_year>/<int:date_month>/<int:date_day>/', views.add_timeslot, name="add_timeslot"),
    path('cancel/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.remove_adopter, name="remove_adopter"),
    path('reschedule_adopter/<int:adopter_id>/new_appt/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/<str:source>/', views.adopter_reschedule, name="adopter_reschedule"),
    path('schedule_next/adopter/<int:adopter_id>/appt/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/<str:source>/', views.greeter_reschedule, name="greeter_reschedule"),
    path("enter_decision/appt/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/", views.enter_decision, name="enter_decision"),
    path('followup/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/<int:host>/', views.send_followup, name="send_followup"),
    path("paperwork/<int:date_year>/<int:date_month>/<int:date_day>/appt/<int:appt_id>/hw/<str:hw_status>/", views.paperwork_calendar, name="paperwork_calendar"),
    path("set_alert/<int:date_year>/<int:date_month>/<int:date_day>/", views.set_alert_date, name="set_alert_date"),
    path("set_alert_greeter/adopter/<int:adopter_id>/<int:date_year>/<int:date_month>/<int:date_day>/", views.set_alert_date_greeter, name="set_alert_date_greeter"),
    path("toggle/<int:appt_id>/<int:date_year>/<int:date_month>/<int:date_day>/", views.toggle_lock, name="toggle_lock"),
    path("toggle_all/<int:date_year>/<int:date_month>/<int:date_day>/<int:lock>/", views.toggle_all, name="toggle_all"),
    path("toggle_time/<int:timeslot_id>/<int:date_year>/<int:date_month>/<int:date_day>/<int:lock>/", views.toggle_time, name="toggle_time"),

    #report pages
    path("reports/home/", views.daily_reports_home, name="daily_reports_home"),
    path("reports/all/<int:date_year>/<int:date_month>/<int:date_day>/", views.daily_report_all_appts, name="daily_report_all_appts"),
    path("reports/adoption_chosen_fta/<int:date_year>/<int:date_month>/<int:date_day>/", views.daily_report_adopted_chosen_fta, name="daily_report_adopted_chosen_fta"),
    path("reports/adoption_chosen_fta/<int:date_year>/<int:date_month>/<int:date_day>/print/", views.report_print, name="report_print"),


    #chosen_board
    path("chosen_board/", views.chosen_board, name="chosen_board"),
    path("chosen_board/clear/<int:appt_id>/", views.remove_from_chosen_board, name="clear_from_cb"),
    path("chosen_board/complete/<int:appt_id>/", views.mark_complete_on_chosen_board, name="mark_complete_cb"),
    path("chosen_board/update/<int:appt_id>/<str:outcome>/", views.cb_update_status, name="cb_update_status")
    ]
