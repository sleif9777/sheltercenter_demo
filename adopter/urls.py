from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="adopter_home"),
    path("faq/", views.faq, name="faq"),
    path("faq/test/", views.faq_test, name="faq_test"),
    path("select/", views.login, name="select_adopter"),
    path("contact/", views.contact, name="contact_us"),
    path("add/", views.add, name="add_adopter"),
    path("acknowledged/", views.acknowledged_faq, name="acknowledged_faq"),
    path("instructions/", views.visitor_instructions, name="visitor_instructions"),
    path('contact_adopter/appt/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/<str:source>/', views.contact_adopter, name="contact_adopter"),
    path('edit/<int:adopter_id>/', views.edit_adopter, name="edit_adopter"),
    path('resend_invite/<int:adopter_id>/', views.resend_invite, name="resend_invite"),
    path('manage/', views.manage, name="adopter_manage"),
    path('set_alert/<int:adopter_id>', views.set_alert_mgr, name="set_alert_mgr")
]
