import copy
import datetime

from django.contrib.auth.models import Group, User
from django.shortcuts import render

from .forms import *
from .models import *
from adopter.forms import ContactUsForm
from adopter.views import generate_auth_code, get_sandbox_email, get_signature_for_contact
from appt_calendar.views import get_groups
from dashboard.decorators import *
from email_mgr.email_sender import *
from email_mgr.models import EmailTemplate

sandbox = str(os.environ.get('SANDBOX')) == "1"
today = datetime.datetime.today()

# Create your views here.
@authenticated_user
@allowed_users(allowed_roles={
        'corp_volunteer_admin', 'corp_volunteer', 'superuser'})
def calendar(request):
    global today

    if 'corp_volunteer' in get_groups(request.user):
        all_future_events = VolunteeringEvent.objects.filter(
            available=True,
            date__gte=today,
        ).order_by('date')
    else:
        all_future_events = VolunteeringEvent.objects.filter(
            date__gte=today,
        ).order_by('date')

    context = {
        'all_future_events': all_future_events
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
    email = copy.deepcopy(org.primary_email)

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
        return event.organization.id != og_org_id
    else:
        if og_org_id:
            og_org = Organization.objects.get(pk=og_org_id)
            event.relist(og_org)
        return False


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


@authenticated_user
@allowed_users(allowed_roles={'corp_volunteer_admin', 'superuser'})
def edit_event(request, event_id):
    event = VolunteeringEvent.objects.get(pk=event_id)
    org = event.organization
    form = EventForm(request.POST or None, instance=event)

    if org:
        og_org = copy.deepcopy(event.organization.id)
        header_text = event.organization.org_name
    else:
        og_org = None
        header_text = event.date_string()

    if form.is_valid():
        org_changed = handle_valid_edit_event_form(form, event, og_org)
        
        if org_changed:
            return redirect('contact_org', event.organization.id, "add")
        else:
            return redirect('event_calendar')
    else:
        form = EventForm(request.POST or None, instance=event)

    context = {
        'form': form,
        'header_text': header_text,
        'page_title': "Edit Event",
    }

    return render(request, "corporate_volunteering/edit_form.html", context)


@authenticated_user
@allowed_users(allowed_roles={'corp_volunteer_admin', 'superuser'})
def add_event(request):
    form = EventForm(request.POST or None)

    if form.is_valid():
        form.save()
        event = VolunteeringEvent.objects.latest('id')
        org_changed = handle_valid_edit_event_form(form, event, None)
        
        if org_changed:
            return redirect('contact_org', event.organization.id, "add")
        else:
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


def get_template_from_source(source, org, signature):
    file1 = None
    file2 = None
    subject = None

    # TO DO
    # create and update templates, add file for waiver

    match source:     
        case 'add':
            template = EmailTemplate.objects.get(
                template_name="Dogs Were Adopted")
        case 'confirm':
            template = EmailTemplate.objects.get(
                template_name="Dogs Were Adopted")
        case 'thank_you':
            template = EmailTemplate.objects.get(
                template_name="Dogs Were Adopted")
        case _:
            template = EmailTemplate.objects.get(
                template_name="Dogs Were Adopted")

    template = replacer(
        template.text.replace('*SIGNATURE*', signature), None, None, org=org)

    return template, file1, file2, subject


@authenticated_user
@allowed_users(allowed_roles={'corp_volunteer_admin', 'superuser'})
def contact_org(request, org_id, source):
    global today
    org = Organization.objects.get(pk=org_id)
    signature = get_signature_for_contact(request.user)
    template, file1, file2, subject = get_template_from_source(
        source, org, signature)

    form = ContactUsForm(
        request.POST or None, initial={'message': template})

    if form.is_valid():
        data = form.cleaned_data
        message = data['message']
        new_contact_org_msg(Organization, message, [file1, file2], subject)
        
        # return redirect to add page

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
