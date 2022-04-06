from django.urls import path
from . import views

urlpatterns = [
    path("<int:adopter_id>/", views.home, name="adopter_home"),
    path("<int:adopter_id>/faq/", views.faq, name="faq"),
    path("select/", views.login, name="select_adopter"),
    path("<int:adopter_id>/contact/", views.contact, name="contact_us"),
    path("add/", views.add, name="add_adopter"),
    path("acknowledged/<int:adopter_id>", views.acknowledged_faq, name="acknowledged_faq"),
    path("<int:adopter_id>/instructions/", views.visitor_instructions, name="visitor_instructions"),
    path('contact_adopter/appt/<int:appt_id>/date/<int:date_year>/<int:date_month>/<int:date_day>/<str:source>/', views.contact_adopter, name="contact_adopter"),
    path('edit/<int:adopter_id>/', views.edit_adopter, name="edit_adopter"),
    path('manage/', views.manage, name="adopter_manage"),
]
