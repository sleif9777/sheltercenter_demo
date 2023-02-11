from django.urls import path

from . import views

urlpatterns = [
    #calendar view pages
    path("", views.calendar, name="calendar"),
    path("?y=<int:date_year>?m=<int:date_month>?d=<int:date_day>/", views.calendar_date, name="calendar_date"),
    path("?y=<int:date_year>?m=<int:date_month>?d=<int:date_day>?appt=<int:appt_id>", views.calendar_date_appt, name="calendar_date_appt"),
    path("?y=<int:date_year>?m=<int:date_month>?d=<int:date_day>?ts=<int:ts_id>", views.calendar_date_ts, name="calendar_date_ts"),
    path("copy?y=<int:date_year>?m=<int:date_month>?d=<int:date_day>", views.copy_temp_to_cal, name="copy_temp_to_cal"),
    path("print?y=<int:date_year>?m=<int:date_month>?d=<int:date_day>", views.calendar_print, name="calendar_print"),
    path('schedule_next?adp=<int:adopter_id>?appt=<int:appt_id>/jump_to_date?s=<str:source>/', views.jump_to_date_greeter, name="jump_to_date_greeter"),
    path("jump_to_date/", views.jump_to_date, name="jump_to_date"),

    #calendar admin pages
    path('edit?appt=<int:appt_id>?y=<int:date_year>?m=<int:date_month>?d=<int:date_day>/', views.edit_appointment, name="edit_cal_appointment"),
    path('edit?appt=<int:appt_id>?y=<int:date_year>?m=<int:date_month>?d=<int:date_day>?s=mgmt', views.edit_appointment_from_mgmt, name="edit_cal_appointment_mgmt"),
    path('book?appt=<int:appt_id>?y=<int:date_year>?m=<int:date_month>?d=<int:date_day>/', views.book_appointment, name="book_cal_appointment"),
    path('delete?appt=<int:appt_id>?y=<int:date_year>?m=<int:date_month>?d=<int:date_day>/', views.delete_appointment, name="delete_cal_appointment"),
    path('add?ts=<int:timeslot_id>?y=<int:date_year>?m=<int:date_month>?d=<int:date_day>/', views.add_appointment, name="add_cal_appointment"),
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
    path("check_in/<int:appt_id>/<int:date_year>/<int:date_month>/<int:date_day>/", views.check_in_appt, name="check_in_appt"),
    path("toggle/<int:appt_id>/<int:date_year>/<int:date_month>/<int:date_day>/", views.toggle_lock, name="toggle_lock"),
    path("toggle_all/<int:date_year>/<int:date_month>/<int:date_day>/<int:lock>/", views.toggle_all, name="toggle_all"),
    path("toggle_time/<int:timeslot_id>/<int:date_year>/<int:date_month>/<int:date_day>/<int:lock>/", views.toggle_time, name="toggle_time"),
    path("open_house_scheduling/", views.open_house_scheduling, name="open_house_scheduling"),

    #report pages
    path("reports/home/", views.daily_reports_home, name="daily_reports_home"),
    path("reports/adoption_chosen_fta/<int:date_year>/<int:date_month>/<int:date_day>/", views.daily_report_adopted_chosen_fta, name="daily_report_adopted_chosen_fta"),
    path("reports/adoption_chosen_fta/<int:date_year>/<int:date_month>/<int:date_day>/print/", views.report_print, name="report_print"),
    path("reports/checked_in_appts/", views.checked_in_appts, name="checked_in_appts"),

    #chosen_board
    path("chosen_board/", views.chosen_board, name="chosen_board"),
    path("chosen_board/clear/<int:appt_id>/", views.remove_from_chosen_board, name="clear_from_cb"),
    path("chosen_board/complete/<int:appt_id>/", views.mark_complete_on_chosen_board, name="mark_complete_cb"),
    path("chosen_board/update/<int:appt_id>/<str:outcome>/", views.cb_update_status, name="cb_update_status"),
    path("chosen_board/no_longer_ready/<int:appt_id>/", views.revert_to_needs_well_check, name="revert_to_needs_well_check"),

    #adopter access pages
    path("request_access?adopter/<int:adopter_id>/", views.request_access, name="request_access"),
    path("allow_access/adopter/<int:adopter_id>/", views.allow_access, name="allow_access"),
    path("surrender/adopter/<int:adopter_id>/", views.surrender_form, name="surrender_form"),
    ]
