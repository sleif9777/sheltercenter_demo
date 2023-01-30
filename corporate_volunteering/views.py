import copy
import datetime
import numpy as np

from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.shortcuts import render

from .forms import *
from .models import *
from adopter.forms import ContactUsForm
from adopter.views import generate_auth_code, get_sandbox_email, get_signature_for_contact
from appt_calendar.views import get_groups
from dashboard.decorators import *
from email_mgr.email_sender import *
from email_mgr.models import EmailTemplate

sandbox = str(os.environ.get('EVENT_SANDBOX')) == "1"
today = datetime.datetime.today()

# Create your views here.
@authenticated_user
@allowed_users(allowed_roles={
        'corp_volunteer_admin', 'corp_volunteer', 'superuser'})
def calendar(request, past=0):
    global today

    if 'corp_volunteer' in get_groups(request.user):
        org = request.user.organization
        events = VolunteeringEvent.objects.filter(
            Q(organization=org) | Q(available=True)
        ).order_by('date')
    else:
        events = VolunteeringEvent.objects.filter(
            marked_as_complete=bool(past),
        ).order_by('date')

    context = {
        'events': events
    }
    
    return render(
        request, "corporate_volunteering/volunteer_schedule.html", context)


@authenticated_user
@allowed_users(allowed_roles={'corp_volunteer_admin', 'superuser'})
def manage_orgs(request):
    organizations = Organization.objects.all()
    context = {
        'organizations': organizations,
        'page_title': "Manage Organizations",
    }
    return render(request, "corporate_volunteering/org_mgmt.html", context)


def book_event(request, event_id):
    event = VolunteeringEvent.objects.get(pk=event_id)
    org = request.user.organization

    event.organization = org
    event.delist()
    event_booked(org, event)

    return redirect("event_calendar")


def create_new_user_from_organization(organization):
    #search for coorporate volunteer and add first
    try:
        new_user = User.objects.get(
            username=organization.contact_email.lower(), 
            email=organization.contact_email,
        )
        if new_user.adopter:
            organization.auth_code = new_user.adopter.auth_code
    #if new, create user
    except:
        new_user = User.objects.create_user(
            username=organization.contact_email.lower(), 
            email=organization.contact_email, 
            password=str(organization.auth_code)
        )

    #assign to adopter and save
    organization.user = new_user
    organization.save()

    corporate_volunteer_group = Group.objects.get(name='corp_volunteer')
    corporate_volunteer_group.user_set.add(new_user)


def add_from_form(organization):
    global sandbox

    if sandbox:
        organization.contact_email = get_sandbox_email(
            organization.leader_fname, organization.leader_lname)

    organization.auth_code = generate_auth_code()
    organization.save()

    create_new_user_from_organization(organization)


@authenticated_user
@allowed_users(allowed_roles={'corp_volunteer_admin', 'superuser'})
def add_organization(request):
    form = OrganizationForm(request.POST or None)

    if form.is_valid():
        try:
            form_data = form.cleaned_data
            org = attempt_to_handle_existing_organization(form_data)
        except:
            form.save()
            org = Organization.objects.latest('id')
            add_from_form(org)

        contact_org(request, org.id, 'add')

    form = OrganizationForm(request.POST or None)

    context = {
        'form': form,
        'page_title': "Add Organization",
    }

    return render(request, "corporate_volunteering/add_orgs.html", context)


@authenticated_user
@allowed_users(allowed_roles={'corp_volunteer_admin', 'superuser'})
def edit_organization(request, org_id):
    org = Organization.objects.get(pk=org_id)
    email = copy.deepcopy(org.contact_email)

    form = OrganizationForm(request.POST or None, instance=org)

    if form.is_valid():
        handle_valid_edit_org_form(form, org, email)
        return redirect('edit_org', org_id)
    else:
        form = OrganizationForm(request.POST or None, instance=org)

    context = {
        'form': form,
        'header_text': org.org_name,
        'page_title': "Edit Organization",
    }

    return render(request, "corporate_volunteering/edit_form.html", context)


def handle_valid_edit_event_form(form, event, og_org_id):
    form.save()
    org = event.organization

    if org:
        event.delist()
    elif og_org_id:
        og_org = Organization.objects.get(pk=og_org_id)
        event.relist(og_org)


def remove_organization(request, event_id):
    event = VolunteeringEvent.objects.get(pk=event_id)
    org = event.organization

    event.relist(org)
    return redirect("event_calendar")


def delete_event(request, event_id):
    event = VolunteeringEvent.objects.get(pk=event_id)
    org = event.organization

    if org:
        event.relist(org)   

    event.delete()
    return redirect("event_calendar")


def get_event_time_form_defaults(event):
    defaults = {
        'start_hour': event.event_start_time.hour,
        'start_minute': event.event_start_time.minute,
        'start_daypart': "0" if event.event_start_time.hour < 12 else "1",
        'end_hour': event.event_end_time.hour,
        'end_minute': event.event_end_time.minute,
        'end_daypart': "0" if event.event_end_time.hour < 12 else "1",
    }
    return defaults


def map_start_and_end(form_data):
    start_hour = int(form_data['start_hour'])
    start_minute = int(form_data['start_minute'])
    if form_data['start_daypart'] == "1" and start_hour < 12:
        start_hour += 12
    start_time = datetime.time(start_hour, start_minute)
    
    end_hour = int(form_data['end_hour'])
    end_minute = int(form_data['end_minute'])
    if form_data['end_daypart'] == "1" and end_hour < 12:
        end_hour += 12   
    end_time = datetime.time(end_hour, end_minute)

    return start_time, end_time


def save_start_end_times(event, timeform_data):
    start_time, end_time = map_start_and_end(timeform_data)
    event.event_start_time = start_time
    event.event_end_time = end_time
    event.save()


@authenticated_user
@allowed_users(allowed_roles={'corp_volunteer_admin', 'superuser'})
def edit_event(request, event_id):
    event = VolunteeringEvent.objects.get(pk=event_id)
    org = event.organization
    form = EventForm(request.POST or None, instance=event)
    get_defaults = get_event_time_form_defaults(event)
    time_form = EventTimeForm(request.POST or None, initial=get_defaults)

    if org:
        og_org = copy.deepcopy(event.organization.id)
        header_text = event.organization.org_name
    else:
        og_org = None
        header_text = event.date_string()

    if form.is_valid() and time_form.is_valid():
        handle_valid_edit_event_form(form, event, og_org)
        timeform_data = time_form.cleaned_data
        save_start_end_times(event, timeform_data)
        
        return redirect('event_calendar')
    else:
        form = EventForm(request.POST or None, instance=event)
        time_form = EventTimeForm(request.POST or None, initial=get_defaults)

    context = {
        'form': form,
        'header_text': header_text,
        'page_title': "Edit Event",
        'time_form': time_form,
    }

    return render(request, "corporate_volunteering/edit_form.html", context)


@authenticated_user
@allowed_users(allowed_roles={'corp_volunteer_admin', 'superuser'})
def add_event(request):
    form = EventForm(request.POST or None)

    if form.is_valid():
        form.save()
        event = VolunteeringEvent.objects.latest('id')
        handle_valid_edit_event_form(form, event, None)
        
        return redirect('event_calendar')
    else:
        form = EventForm(request.POST or None)

    context = {
        'form': form,
        'header_text': "Add Event",
        'page_title': "Add Event",
    }

    return render(request, "corporate_volunteering/edit_form.html", context)


def handle_valid_edit_org_form(form, org, og_email):
    form.save()
    
    email_changed = org.contact_email != og_email

    if email_changed:
        org.user.username = str(org.contact_email)

        if org.user.adopter:
            org.user.adopter.primary_email = org.contact_email
            org.user.adopter.save()

        org.user.save()


def get_template_from_source(source, signature, org, event=None):
    file1 = None
    file2 = None
    subject = None

    match source:     
        case 'add':
            template = EmailTemplate.objects.get(
                template_name="Invite Organization")
        case 'confirm':
            template = EmailTemplate.objects.get(
                template_name="Confirm Event")
        #case waiver?
        case 'thank_you':
            template = EmailTemplate.objects.get(
                template_name="Thank Organization")
        case _:
            template = EmailTemplate.objects.get(
                template_name="Contact Organization")

    template = replacer(
        template.text.replace(
            '*SIGNATURE*', signature), None, None, org=org, event=event)

    return template, file1, file2, subject


@authenticated_user
@allowed_users(allowed_roles={'corp_volunteer'})
def contact_team(request, event_id=None):
    if event_id:
        event = VolunteeringEvent.objects.get(pk=event_id)
        d_string = event.date_string()
        default_message = "I would like to reschedule my event for for {0}...".format(d_string)
    else:
        event = None
        default_message = ""

    form = ContactUsForm(
        request.POST or None, 
        initial={'message': default_message}
    )

    if form.is_valid():
        org = request.user.organization
        message = form.cleaned_data['message']
        new_contact_volunteer_event_team_msg(org, message, event)
        return redirect('event_calendar')

    context = {
        'events': True,
        'form': form,
        'page_title': "Contact Us",
    }

    return render(request, "adopter/contactteam.html", context)


@authenticated_user
@allowed_users(allowed_roles={'corp_volunteer_admin', 'superuser'})
def contact_org(request, org_id, source, event_id=None):
    global today
    org = Organization.objects.get(pk=org_id)
    signature = get_signature_for_contact(request.user)

    if event_id:
        event = VolunteeringEvent.objects.get(pk=event_id)
    else:
        event = None

    template, file1, file2, subject = get_template_from_source(
        source, signature, org, event)

    form = ContactUsForm(
        request.POST or None, initial={'message': template})

    if form.is_valid():
        data = form.cleaned_data
        message = data['message']
        new_contact_org_msg(Organization, message, [file1, file2], subject)

        return redirect("add_org")
        
    context = {
        'form': form,
        'page_title': "Contact {0}".format(org.org_name),
    }

    return render(request, "adopter/contactadopter.html", context)


def attempt_to_handle_existing_organization(form_data):
    fname = form_data["leader_fname"]
    lname = form_data["leader_lname"]
    primary_email = form_data["contact_email"]

    email_for_search = get_email_from_form(fname, lname, primary_email)
    existing_org = attempt_to_retrieve_existing_org(email_for_search)

    return existing_org


def get_email_from_form(f_name, l_name, email):
    global sandbox
    if sandbox:
        return get_sandbox_email(f_name, l_name)
    else:
        return email.lower()


def attempt_to_retrieve_existing_org(email_for_search):
    try:
        existing_user = User.objects.get(username=email_for_search)
        existing_organization = Organization.objects.get(user=existing_user)
    except:
        existing_organization = Organization.objects.filter(
            contact_email=email_for_search).latest('id')

    if existing_organization:
        return existing_organization
    else:
        raise AttributeError


def mark_event(request, event_id, flag):
    event = VolunteeringEvent.objects.get(pk=event_id)

    match flag:
        case "donation":
            event.donation_received = not event.donation_received
        case "waivers":
            event.waivers_complete = not event.waivers_complete
        case "social_media":
            event.posted_social_media = not event.posted_social_media
        case "thank_you":
            event.sent_thank_you = not event.sent_thank_you
        case "complete":
            event.marked_as_complete = not event.marked_as_complete

    event.save()

    return redirect("event_calendar")