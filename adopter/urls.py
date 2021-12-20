from django.urls import path
from . import views

urlpatterns = [
    path("<int:adopter_id>/", views.home, name="adopter_home"),
    path("<int:adopter_id>/faq/", views.faq, name="faq"),
    path("select/", views.login, name="select_adopter"),
    path("<int:adopter_id>/contact/", views.contact, name="contact_us"),
    path("appt/<int:appt_id>/dogs_were_adopted/", views.send_dogs_were_adopted_msg, name="dogs_were_adopted"),
    path("appt/<int:appt_id>/limited_matches/<str:description>/date/<int:date_year>/<int:date_month>/<int:date_day>/", views.send_limited_matches_msg, name="limited_matches"),
    #path("<int:adopter_id>/send_dates_open_msg/date/<int:date_year>/<int:date_month>/<int:date_day>/", views.send_dates_open_msg, name="send_dates_open_msg"),
    #path("decision/<int:adopter_id>/", views.adopter_decision, name="adopter_decision"),
    #path("add/", views.add_adopter, name="add_adopter")
    path("add/", views.add, name="add_adopter"),
    path("acknowledged/<int:adopter_id>", views.acknowledged_faq, name="acknowledged_faq"),
    path("<int:adopter_id>/instructions/", views.visitor_instructions, name="visitor_instructions"),
    path('contact_adopter/appt/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/', views.contact_adopter, name="contact_adopter")
]
