from django.urls import path

from . import views

urlpatterns = [
    path("", views.calendar, name="event_calendar"),
    path("manage_orgs/", views.manage_orgs, name="manage_orgs"),
    path("add/", views.add_organization, name="add_org"),
    path("add_event/", views.add_event, name="add_event"),
    path("edit_event/<int:event_id>/", views.edit_event, name="edit_event"),
    path("edit_org/<int:org_id>", views.edit_organization, name="edit_org"),
    path("remove_org/<int:event_id>/", views.remove_organization, name="remove_organization"),
    path("delete_event/<int:event_id>", views.delete_event, name="delete_event"),
    path("contact?org=<int:org_id>?source=<str:source>/", views.contact_org, name="contact_org")
]