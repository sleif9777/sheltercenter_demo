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
        )
    else:
        all_future_events = VolunteeringEvent.objects.filter(
            date__gte=today,
        )

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
            username=organization.primary_email.lower(), 
            email=organization.primary_email,
        )
        if new_user.adopter:
            organization.auth_code = new_user.adopter.auth_code
    #if new, create user
    except:
        new_user = User.objects.create_user(
            username=organization.primary_email.lower(), 
            email=organization.primary_email, 
            password=str(organization.auth_code)
        )

    #assign to adopter and save
    organization.user = new_user
    organization.save()

    corporate_volunteer_group = Group.objects.get(name='corporate_volunteer')
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
    global today
    form = AddOrganizationForm(request.POST or None)

    if form.is_valid():
        try:
            form_data = form.cleaned_data
            org = attempt_to_handle_existing_organization(form_data)
        except:
            form.save()
            org = Organization.objects.latest('id')
            add_from_form(org)

        contact_org(request, org.id, 'add')

    form = AddOrganizationForm(request.POST or None)

    context = {
        'form': form,
        'page_title': "Add Adopters",
        'today': today,
    }

    return render(request, "corporate_volunteering/add_orgs.html", context)


def get_template_from_source(source, org, signature):
    file1 = None
    file2 = None
    subject = None

    # TO DO
    # create and update templates, add file for waiver

    match source:     
        case 'add':
            template = EmailTemplate.objects.get(
                template_name="")
        case 'confirm':
            template = EmailTemplate.objects.get(
                template_name="")
        case 'thank_you':
            template = EmailTemplate.objects.get(
                template_name="")
        case _:
            template = EmailTemplate.objects.get(
                template_name="")

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

    return existing_organization
