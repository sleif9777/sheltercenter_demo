from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='visit_comms'),

    path('add/faq/sec/<int:sec_id>/', views.add_faq, name='add_faq'),
    path('edit/faq/<int:faq_id>/', views.edit_faq, name='edit_faq'),
    path('delete/faq/<int:faq_id>/', views.delete_faq, name='delete_faq'),

    path('add/instr/', views.add_visitor_instr, name='add_visitor_instr'),
    path('edit/instr/<int:instr_id>/', views.edit_visitor_instr, name='edit_visitor_instr'),
    path('delete/instr/<int:instr_id>/', views.delete_visitor_instr, name='delete_visitor_instr'),

    path('add/faq_section/', views.add_faq_section, name='add_faq_section'),
]
