from django.urls import path

from . import views

urlpatterns = [
    path("", views.calendar, name="event_calendar"),
    path("manage_orgs/", views.manage_orgs, name="manage_orgs"),
    path("add/", views.add_organization, name="add_org"),
    path("add_event/", views.add_event, name="add_event"),
    path("edit_event?event=<int:event_id>/", views.edit_event, name="edit_event"),
    path("book_event?event=<int:event_id>/", views.book_event, name="book_event"),
    path("?past=<int:past>/", views.calendar, name="past_events"),
    path("edit_org?org=<int:org_id>", views.edit_organization, name="edit_org"),
    path("remove_org?event=<int:event_id>/", views.remove_organization, name="remove_organization"),
    path("delete_event?event=<int:event_id>", views.delete_event, name="delete_event"),
    path("contact?org=<int:org_id>?source=<str:source>/", views.contact_org, name="contact_org"),
    path("contact?org=<int:org_id>?source=<str:source>/event=<int:event_id>/", views.contact_org, name="contact_org_event"),
    path("contact_team/", views.contact_team, name="contact_corp_volunteer_team"),
    path("contact_team?event=<int:event_id>/", views.contact_team, name="contact_corp_volunteer_team_reschedule"),
    path("mark_event?event=<int:event_id>?flag=<str:flag>/", views.mark_event, name="mark_event"),
]