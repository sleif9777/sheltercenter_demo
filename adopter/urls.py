from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="adopter_home"),
    path("faq/", views.faq, name="faq"),
    path("faq/test/", views.faq_test, name="faq_test"),
    path("contact/", views.contact, name="contact_us"),
    path("contact/<int:appt_id>", views.contact, name="contact_us"),
    path("contact/<str:dog_name>", views.contact, name="contact_us"),
    path("add/", views.add, name="add_adopter"),
    path("open_house_add/", views.open_house_add_adopter, name="open_house_add_adopter"),
    path("reconcile/", views.reconcile_missing_users, name="reconcile"),
    path("upload_error/", views.too_many_rows, name="too_many_rows"),
    path("acknowledged/", views.acknowledged_faq, name="acknowledged_faq"),
    path("instructions/", views.visitor_instructions, name="visitor_instructions"),
    path('contact_adopter/appt/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/<str:source>/', views.contact_adopter, name="contact_adopter"),
    path('resend_confirmation/<int:appt_id>/', views.resend_confirmation, name='resend_confirmation'),
    path('edit/<int:adopter_id>/', views.edit_adopter, name="edit_adopter"),
    path('edit/<int:adopter_id>/<int:alert>/', views.edit_adopter, name="edit_adopter_alert"),
    path('resend_invite/<int:adopter_id>/', views.resend_invite, name="resend_invite"),
    path('send_to_inactive/', views.send_to_inactive, name="send_to_inactive"),
    path('manage/', views.manage, name="adopter_manage"),
    path('stage_import/', views.stage_import, name="stage_import"),
    path('set_alert/<int:adopter_id>', views.set_alert_mgr, name="set_alert_mgr"),
]
