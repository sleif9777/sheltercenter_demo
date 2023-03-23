import copy
import csv
import datetime
import os
import requests
import sys
import time

from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from random import randint

from .adopter_manager import *
from .forms import *
from .models import *
from appt_calendar.models import Appointment
from dashboard.decorators import *
from email_mgr.dictionary import *
from email_mgr.email_sender import *
from email_mgr.models import *
from schedule_template.models import *
from visit_and_faq.models import *

adopter_upload_settings = AdopterUploadSettings.objects.get(pk=1)
api_root = "https://www.shelterluv.com/api/v1/"
sandbox = str(os.environ.get('SANDBOX')) == "1"
system_settings = SystemSettings.objects.get(pk=1)

# Create your views here.

def get_email_from_row(row):
    # generates either a test email address or processes
    # the email values in the row
    global sandbox

    if sandbox:
        f_name = row[13]
        l_name = row[14]
        primary_email = get_sandbox_email(f_name, l_name)
        secondary_email = ""
    #else use real email
    else:
        primary_email = row[28].lower()
        secondary_email = row[29].lower()

    return primary_email, secondary_email


def generate_auth_code():
    # generates an auth code for the adopter to use for login
    auth_code = randint(100000, 999999)

    while auth_code % 100 == 0:
        auth_code = randint(100000, 999999)

    return auth_code 


def match_status(row):
    # returns a number to match an approval/block status
    match row[4]:
        case "Denied":
            return "2"
        case ["Pending", "In Process"]:
            return "3"
        case _:
            return "1"


def create_adopter_from_row(row):
    primary_email, secondary_email = get_email_from_row(row)
    auth_code = generate_auth_code()
    status = match_status(row)

    new_adopter = Adopter.objects.create(
        activity_level = row[32],
        app_interest = row[11],
        application_id = row[0],
        auth_code = auth_code,
        city = row[18].title(),
        f_name = row[13].title(),
        has_fence = True if row[45] == "Yes" else False,
        housing = row[35],
        housing_type = row[33],
        l_name = row[14].title(),
        lives_with_parents = True if row[35] == "Live with Parents" else False,
        out_of_state = False if row[19] == "NC" else True,
        phone_number = row[22],
        primary_email = primary_email,
        secondary_email = secondary_email,
        state = row[19],
        status = status
    )

    return new_adopter


def create_new_user_from_adopter(adopter):
    #search for coorporate volunteer and add first
    try:
        new_user = User.objects.get(
            username=adopter.primary_email.lower(), 
            email=adopter.primary_email,
        )

        print("located user #{0}".format(new_user.id))

        if new_user.organization:
            adopter.auth_code = new_user.organization.auth_code
    #if new, create user
    except:
        new_user = User.objects.create_user(
            username=adopter.primary_email.lower(), 
            email=adopter.primary_email, 
            password=str(adopter.auth_code)
        )
        # except IntegrityError:
        #     attach_existing_user_to_adopter(adopter)
        # except:
        #     pass

    #assign to adopter and save
    adopter.user = new_user
    adopter.save()

    adopter_group = Group.objects.get(name='adopter')
    adopter_group.user_set.add(new_user)


def reconcile_missing_users(request, generate_email=False):
    affected_adopters = Adopter.objects.filter(user=None)
    print("Attempting to reconcile {0} adopters".format(len(affected_adopters)))

    for adopter in affected_adopters:
        try:
            create_new_user_from_adopter(adopter)
            print("Created user for {0}".format(adopter.full_name()))
        except IntegrityError:
            attach_existing_user_to_adopter(adopter, generate_email)
            print("Attached user for {0}".format(adopter.full_name()))
        except:
            print("Could not create user for {0}".format(adopter.full_name()))

    if not generate_email:
        return redirect('add_adopter')


def attach_existing_user_to_adopter(adopter, generate_email=False):
    user = User.objects.get(username=adopter.primary_email.lower())

    try:
        adopter_with_user = Adopter.objects.get(user=user)
        if generate_email:
            create_invite_email(adopter_with_user)
        # adopter.delete() #TO DO: transfer attribute data from new to old
        return adopter_with_user
    except:
        adopter.user = user
        adopter.save()

        adopter_group = Group.objects.get(name='adopter')
        adopter_group.user_set.add(user)


def eval_unique_app_interest(response):
    return response not in ["", "dogs", "Dogs", "dog", "Dog"]


def eval_app_interest(response):
    # evaluates whether app interest should be included in subject line
    unique = eval_unique_app_interest(response)
    short = len(response) <= 10

    return True if unique and short else False


@authenticated_user
@allowed_users(allowed_roles={'superuser'})
def login(request):
    adopters = Adopter.objects.all()

    context = {
        'adopters': adopters,
        'page_title': "Log In",
    }

    return render(request, "adopter/login.html", context)


def home_page(request):
    return redirect('login')


def create_invite_email(adopter, inactive=False):
    message = PendingMessage()
    message.email = adopter.primary_email

    if inactive:
        message.subject = "Are you ready to schedule your appointment?"
        template = EmailTemplate.objects.get(
            template_name="Are you ready to schedule your appointment?")
    else:        
        include_app_interest = eval_app_interest(adopter.app_interest)
        message.subject = "Your adoption request has been reviewed: {0}".format(
            adopter.full_name().upper())

        if include_app_interest:
            message.subject += " ({0})".format(adopter.app_interest)

        if adopter.out_of_state:
            template = EmailTemplate.objects.get(
                template_name="Application Accepted (outside NC, VA, SC)")
        else:
            template = EmailTemplate.objects.get(
                template_name="Application Accepted (inside NC, VA, SC)")

    html = replacer(template.text, adopter, None)
    text = strip_tags(html)

    message.html = html
    message.text = text
    message.save()


def is_special_circumstances(adopter):
    return (adopter.adopting_foster or 
            adopter.friend_of_foster or 
            adopter.adopting_host)


def handle_existing(existing_adopter, status, app_interest):
    today = datetime.date.today()
    last_4_days = [date_delta(x) for x in range(4)]
    one_year_ago = today - datetime.timedelta(days=365)
    accepted_last_4_days = existing_adopter.accept_date in last_4_days
    accepted_over_1_year = existing_adopter.accept_date < one_year_ago

    accepted_adopter_status = accepted_status(existing_adopter)
    pending_adopter_status = existing_adopter.status == "3"
    accepted_app_status = status in ["1", "Accepted"]
    special_circumstances = is_special_circumstances(existing_adopter)

    process = (accepted_app_status and not
               accepted_last_4_days and not
               special_circumstances)
    unique_app_interest = eval_unique_app_interest(app_interest)

    if process:
        #if the adopter is approved...
        if accepted_adopter_status:
            existing_adopter.accept_date = today

            if unique_app_interest:
                existing_adopter.app_interest = app_interest

        #elif moved from pending to approved, send invite
        elif pending_adopter_status:
            existing_adopter.status = "1"
            
        existing_adopter.save()
        create_invite_email(existing_adopter)


def remove_spaces_and_lower(f_name, l_name):
    f_name = f_name.replace(" ", "").lower()
    l_name = l_name.replace(" ", "").lower()
    return f_name, l_name


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def too_many_rows(request):
    return render(request, "adopter/too_many_rows.html")


def attempt_to_handle_existing_from_file(row):
    email_for_search = get_email_from_row(row)[0]
    existing_adopter = attempt_to_retrieve_existing_adopter(
        email_for_search)

    # print("Located record for ", existing_adopter)

    #update to newest application
    # existing_adopter.application_id = row[0]
    # existing_adopter.save()
    update_app_details_from_row(existing_adopter.id, row)

    #if blocked, add to error report
    if existing_adopter.status == "2":
        return existing_adopter
    else:
        handle_existing(existing_adopter, row[4], row[11])
        return False


def handle_new_from_file(row):
    adopter = create_adopter_from_row(row)
    
    try:
        create_new_user_from_adopter(adopter)
    except Exception as g:
        # print("ExceptionG: ", g)
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno)
        pass

    if accepted_status(adopter):
        create_invite_email(adopter)
        return False
    else:
        return adopter


def add_from_file(request, file):
    decoded_file = file.read().decode('utf-8').splitlines()
    adopter_data = list(csv.reader(decoded_file))[1:]
    errors = []

    if len(adopter_data) > 100:
        return True
    else:
        for row in adopter_data:
            # print("Starting on ", row[28])
            try:
                error = attempt_to_handle_existing_from_file(row)
                # print("User previously existed")
            except Exception as f:
                # print("ExceptionF: ", f)
                # exc_type, exc_obj, exc_tb = sys.exc_info()
                # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                # print(exc_type, fname, exc_tb.tb_lineno)
                error = handle_new_from_file(row)
                # print('New user added', error)

            if error is not False:
                errors += [error]

        if len(errors) > 0:
            upload_errors(errors)

        return redirect('outbox')


def accepted_status(adopter):
    return adopter.status in ["1", "Accepted"]


def add_from_form(adopter):
    global sandbox

    if sandbox:
        adopter.primary_email = get_sandbox_email(
            adopter.f_name, adopter.l_name)

    adopter.auth_code = generate_auth_code()
    adopter.save()

    if accepted_status(adopter):
        try:
            create_new_user_from_adopter(adopter)
            if is_special_circumstances(adopter):
                shellappt = create_shell_appt(adopter)
                return shellappt
            else:
                return None
        except:
            pass


def open_house_add_adopter(request):
    form = AdopterOpenHouseForm(request.POST or None)
    sign_up_valid = False

    if form.is_valid():
        form_data = form.cleaned_data
        try:
            form_data = form.cleaned_data
            adopter = attempt_to_handle_existing_user(form_data, open_house=True)
        except:
            form.save()
            adopter = Adopter.objects.latest('id')
            add_from_form(adopter)

        adopter.open_house_appt = True
        adopter.open_house_signup_timestamp = datetime.datetime.now()
        adopter.save()

        sign_up_valid = True

    form = AdopterOpenHouseForm()

    context = {
        'form': form,
        'page_title': "Open House Appointment Sign-Up",
        'sign_up_valid': sign_up_valid
    }

    return render(request, "adopter/simple_add_form.html", context)


def create_shell_appt(adopter):
    shellappt = Appointment()
    shellappt.time = datetime.datetime.now()
    shellappt.adopter = adopter
    shellappt.dog = adopter.chosen_dog
    shellappt.outcome = "3"

    shellappt.save()

    adopter.has_current_appt = False
    adopter.acknowledged_faq = True
    adopter.save()

    return shellappt


def get_sandbox_email(f_name, l_name):
    f_name, l_name = remove_spaces_and_lower(f_name, l_name)
    return "sheltercenterdev+{0}{1}@gmail.com".format(f_name, l_name)


def get_email_from_form(f_name, l_name, email):
    global sandbox
    if sandbox:
        return get_sandbox_email(f_name, l_name)
    else:
        return email.lower()


def attempt_to_retrieve_existing_adopter(email_for_search):
    try:
        existing_user = User.objects.get(username=email_for_search)
        existing_adopter = Adopter.objects.get(user=existing_user)
    except:
        existing_adopter = Adopter.objects.filter(primary_email=email_for_search).latest('id')

    return existing_adopter


def attempt_to_handle_existing_user(form_data, open_house=False):
    fname = form_data["f_name"]
    lname = form_data["l_name"]
    primary_email = form_data["primary_email"]

    if not open_house:
        status = form_data["status"]
        app_interest = form_data["app_interest"]

    email_for_search = get_email_from_form(fname, lname, primary_email)
    existing_adopter = attempt_to_retrieve_existing_adopter(email_for_search)

    blocked = existing_adopter.status == "2"
    if not blocked:
        if open_house:
            return existing_adopter
        else:
            handle_existing(existing_adopter, status, app_interest)


def redirect_to_contact(appt, exemption):
    return redirect('contact_adopter', appt.id, appt.date.year, 
                        appt.date.month, appt.date.day, exemption)


def handle_redirect_from_add_form(adopter, shellappt):
    if adopter.adopting_foster:
        redirect_to_contact(shellappt, 'add_form_adopting_foster')
    elif adopter.friend_of_foster:
        redirect_to_contact(shellappt, 'add_form_friend_of_foster')
    elif adopter.adopting_host:
        redirect_to_contact(shellappt, 'add_form_adopting_host')
    elif adopter.carryover_shelterluv:
        carryover_temp(adopter)
    else:
        invite(adopter)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add(request):
    today = datetime.date.today()
    form = AdopterForm(request.POST or None)

    # print(request.FILES)

    #try adding from file
    try:
        if request.method == 'POST' and request.FILES['app_file']:
            file = request.FILES['app_file']
            # can return either boolean or redirect
            too_long = add_from_file(request, file)
            if type(too_long) == bool:
                return render(request, "adopter/too_many_rows.html")
    #except no file, add manually without application
    except:
        if form.is_valid():
            try:
                form_data = form.cleaned_data
                attempt_to_handle_existing_user(form_data)
            except:
                form.save()
                adopter = Adopter.objects.latest('id')
                shellappt = add_from_form(adopter)
                
                if accepted_status(adopter):
                    handle_redirect_from_add_form(adopter, shellappt)

    form = AdopterForm()

    context = {
        'form': form,
        'page_title': "Add Adopters",
        'today': today,
    }

    return render(request, "adopter/addadopterform.html", context)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def manage(request):
    get_feed_of_shelterluv_people()

    adopters = Adopter.objects.all()
    context = {
        'adopters': adopters,
        'page_title': "Manage Adopters",
    }
    return render(request, "adopter/adoptermgmt.html", context)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def send_to_inactive(request):
    add_date = datetime.date.today() - datetime.timedelta(days = 5)
    adopters = Adopter.objects.filter(
        accept_date=add_date,
        acknowledged_faq=False,
        status="1"
    )

    for adopter in adopters:
        create_invite_email(adopter, inactive=True)

    return redirect('adopter_manage')


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def resend_invite(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)
    invite(adopter)
    return redirect('adopter_manage')


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def resend_confirmation(request, appt_id):
    appt = Appointment.objects.get(pk=appt_id)
    date = appt.date
    confirm_etemp(appt.adopter, appt)
    return redirect(
        'calendar_date_appt', date.year, date.month, date.day, appt.id)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def set_alert_mgr(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)
    form = SetAlertDateForm(request.POST or None, instance=adopter)

    if form.is_valid():
        form.save()
        alert_date_set(adopter, adopter.alert_date)
        return redirect('adopter_manage')
    else:
        form = SetAlertDateForm(request.POST or None, instance=adopter)

    context = {
        'adopter': adopter,
        'form': form,
        'page_title': "Set Reminder",
    }

    return render(request, "adopter/set_alert_date.html", context)


def handle_valid_edit_adopter_form(form, adopter, og_status, og_email):
    form.save()
    
    email_changed = adopter.primary_email != og_email
    status_changed = adopter.status != og_status
    status_approved = accepted_status(adopter)
    changed_to_approved = status_changed and status_approved

    if changed_to_approved:
        invite(adopter)

    if email_changed:
        adopter.user.username = str(adopter.primary_email)

        if adopter.user.organization:
            adopter.user.organization.contact_email = adopter.primary_email
            adopter.user.organization.save()

        adopter.user.save()


def get_current_appt_info(adopter):
    try:
        current_appt = Appointment.objects.filter(adopter=adopter).latest('date')
        current_appt_str = current_appt.date_and_time_string()
        date = current_appt.date
    except:
        current_appt = None
        current_appt_str = None
        date = None   

    return current_appt, current_appt_str, date


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_adopter(request, adopter_id, alert=False):
    adopter = Adopter.objects.get(pk=adopter_id)
    status = copy.deepcopy(adopter.status)
    email = copy.deepcopy(adopter.primary_email)
    source = 'mgmt_{0}'.format(str(adopter.id))

    form = AdopterForm(request.POST or None, instance=adopter)
    current_appt, current_appt_str, date = get_current_appt_info(adopter)

    if form.is_valid():
        handle_valid_edit_adopter_form(form, adopter, status, email)
        return redirect('adopter_manage')
    else:
        form = AdopterForm(request.POST or None, instance=adopter)

    context = {
        'adopter': adopter,
        'alert': alert,
        'appt': current_appt,
        'appt_str': current_appt_str,
        'date': date,
        'form': form,
        'page_title': "Edit Adopter",
        'schedulable': ["1", "2", "3"],
        'show_timestr': True,
        'source': source,
        'today': datetime.date.today(),
    }

    return render(request, "adopter/edit_adopter.html", context)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'adopter'})
def faq(request):
    faq_dict = {}

    for sec in FAQSection.objects.all().iterator():
        faq_dict[sec] = [q for q in sec.questions.iterator()]

    context = {
        'faq_dict': faq_dict,
        'page_title': "FAQ",
    }

    return render(request, "adopter/faq.html", context)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'adopter'})
def faq_test(request):
    faq_dict = {}

    for sec in FAQSection.objects.all().iterator():
        faq_dict[sec] = [q for q in sec.questions.iterator()]

    context = {
        'faq_dict': faq_dict,
        'page_title': "FAQ",
    }

    return render(request, "adopter/faq_test_harness.html", context)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'adopter'})
def visitor_instructions(request):
    all_instrs = VisitorInstruction.objects.all()
    context = {
        'all_instrs': all_instrs,
        'page_title': "Visit Instructions",
    }

    return render(request, "adopter/visitor_instructions.html", context)


@authenticated_user
@allowed_users(allowed_roles={'adopter'})
def contact(request, appt_id=None, dog_name=None):
    if appt_id:
        dt_string = Appointment.objects.get(pk=appt_id).date_and_time_string()
        default_message = "I would like to book for {0}.".format(dt_string)
    elif dog_name:
        default_message = "I am interested in meeting {0} (available by appointment only). My availability is [date & time 1], [date & time 2], date & time 3]...".format(dog_name)
    else:
        default_message = ""

    form = ContactUsForm(
        request.POST or None, 
        initial={'message': default_message}
    )

    if form.is_valid():
        adopter = request.user.adopter
        message = form.cleaned_data['message']
        new_contact_us_msg(adopter, message, appt_id)
        return redirect('adopter_home')

    context = {
        'form': form,
        'page_title': "Contact Us",
    }

    return render(request, "adopter/contactteam.html", context)


def get_template_from_source(source, adopter, appt, signature):
    file1 = None
    file2 = None
    subject = None

    match source:     
        case 'cough':
            template_record = "Update for Adopter: Cough"
        case 'nasal_discharge':
            template_record = "Update for Adopter: Nasal Discharge"
        case 'no_longer_ready':
            template_record = "Update for Adopter: No Longer Ready"        
        case "ready_positive":
            template_record = "Ready to Roll (Heartworm Positive)"
            template = EmailTemplate.objects.get(template_name=template_record)
            subject = "{0} is ready to come home!".format(appt.dog)
            file1 = template.file1
            file2 = template.file2
        case "confirm_appt":
            template_record = "Appointment Confirmation"
            subject = "Your appointment is confirmed: {0}".format(
                adopter.full_name().upper())
        case "ready_negative":
            template_record = "Ready to Roll (Heartworm Negative)"
            subject = "{0} is ready to come home!".format(appt.dog)
        case "limited_puppies":
            template_record = "Limited Puppies"
        case "limited_small":
            template_record = "Limited Small Dogs"
        case "limited_small_puppies":
            template_record = "Limited Small Breed Puppies"
        case "limited_hypo":
            template_record = "Limited Hypo"
        case 'dogs_were_adopted':
            template_record = "Watch List (BETA)"
        case 'dog_in_extended_host':
            template_record = "Dog In Extended Host"
        case 'dog_in_medical_foster':
            template_record = "Dog In Medical Foster"
        case 'dog_is_popular_x_in_line':
            template_record = "Dog Is Popular (X in Line)"
        case 'dog_is_popular_low_chances':
            template_record = "Dog Is Popular (Low Chances)"
        case 'dog_not_here_yet':
            template_record = "Dog Not Here Yet"
        case 'add_form_adopting_foster':
            template_record = "Application Accepted (Adopting Foster)"
        case 'add_form_friend_of_foster':
            template_record = "Application Accepted (Friend of Foster)"
        case 'add_form_adopting_host':
            template_record = "Application Accepted (Host Weekend)"
        case 'reminder_breed':
            template_record = "Reminder: Breed Restrictions"
        case 'reminder_parents':
            template_record = "Reminder: Lives With Parents"
        case _:
            template_record = "Contact Adopter"

    template = EmailTemplate.objects.get(template_name=template_record)
    template = replacer(
        template.text.replace('*SIGNATURE*', signature), adopter, appt)

    return template, file1, file2, subject


def get_redirect(source):
    add_source = "add_form" in source
    calendar_source = source in [
        'add_form_adopting_host',
        'calendar', 
        'confirm_appt', 
        'dogs_were_adopted', 
        'dog_in_extended_host', 
        'dog_in_medical_foster', 
        'dog_is_popular', 
        'dog_is_popular_low_chances', 
        'dog_not_here_yet', 
        'limited_hypo', 
        'limited_puppies', 
        'limited_small', 
        'limited_small_puppies', 
        'reminder_breed', 
        'reminder_parents'
    ]
    chosen_board_source = source in [
        "cough",
        "nasal_discharge",
        'no_longer_ready',
        "ready_positive", 
        "ready_negative", 
        "update"
    ]
    mgmt_source = "mgmt" in source

    if add_source:
        return "add_adopter"
    elif calendar_source:
        return "calendar_date_appt"
    elif chosen_board_source:
        return "chosen_board"
    elif mgmt_source:
        return "edit_adopter"


def get_adopter_for_contact(source, appt):    
    if 'mgmt' not in source:
        adopter = appt.adopter
    else:
        adopter_id = source.split('_')[1]
        adopter = Adopter.objects.get(pk=adopter_id)
    
    return adopter


def get_signature_for_contact(user):
    try:
        user_for_signature = user.profile
    except:
        user_for_signature = User.objects.get(username="base").profile

    return user_for_signature.signature


def update_cb_attributes_after_contact(source, appt):
    appt.last_update_sent = today
    appt.all_updates_sent.insert(0, date_str(today))

    if source in ['ready_positive', 'ready_negative']:
        appt.outcome = "7"
        appt.rtr_notif_date = "{0} {1}".format(
            date_no_weekday_str(today), 
            time_str(datetime.datetime.now())
        )

    if source == 'ready_positive':
        appt.heartworm = True

    appt.save()


def update_comm_attributes_after_contact(source, appt):
    match source:
        case "dogs_were_adopted":
            appt.comm_adopted_dogs = True
        case "dog_in_extended_host":
            appt.comm_dog_in_extended_host = True
        case "dog_in_medical_foster":
            appt.comm_dog_in_medical_foster = True
        case "dog_is_popular":
            appt.comm_dog_is_popular = True
        case "dog_is_popular_low_chances":
            appt.comm_dog_is_popular_low_chances = True
        case "dog_not_here_yet":
            appt.comm_dog_not_here_yet = True
        case "limited_hypo":
            appt.comm_limited_hypo = True
        case "limited_puppies":
            appt.comm_limited_puppies = True
        case "limited_small":
            appt.comm_limited_small = True
        case "limited_small_puppies":
            appt.comm_limited_small_puppies = True
        case 'reminder_breed':
            appt.comm_reminder_breed = True
        case 'reminder_parents':
            appt.comm_reminder_parents = True

    appt.save()


def get_appt_for_contact(appt_id):
    try:
        appt = Appointment.objects.get(pk=appt_id)
    except:
        appt = None

    return appt  
            

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def contact_adopter(request, appt_id, date_year, date_month, date_day, source):
    today = datetime.date.today()
    appt = get_appt_for_contact(appt_id)
    adopter = get_adopter_for_contact(source, appt)
    redirect_type = get_redirect(source)
    signature = get_signature_for_contact(request.user)
    template, file1, file2, subject = get_template_from_source(
        source, adopter, appt, signature)

    form = ContactAdopterForm(
        request.POST or None, initial={'message': template})

    if form.is_valid():
        data = form.cleaned_data
        message = data['message']
        new_contact_adopter_msg(adopter, message, [file1, file2], subject)
        
        match redirect_type:
            case "add_adopter":
                return redirect('add_adopter')
            case "calendar_date_appt":
                update_comm_attributes_after_contact(source, appt)
                return redirect('calendar_date_appt',
                    date_year, date_month, date_day, appt.id)
            case "chosen_board":
                update_cb_attributes_after_contact(source, appt)
                return redirect('chosen_board')
            case "edit_adopter":
                return redirect('edit_adopter', adopter.id)

    context = {
        'appt': appt,
        'form': form,
        'page_title': "Contact {0}".format(adopter.full_name()),
    }

    return render(request, "adopter/contactadopter.html", context)


@authenticated_user
@allowed_users(allowed_roles={'adopter'})
def home(request):
    adopter = request.user.adopter
    blocked = adopter.status == "2"

    faq_dict = {}

    for sec in FAQSection.objects.all().iterator():
        faq_dict[sec] = [q for q in sec.questions.iterator()]

    context = {
        'adopter': adopter,
        'faq_dict': faq_dict,
        'first_name': adopter.f_name,
        'full_name': adopter.full_name(),
        'page_title': "Home",
    }

    if blocked:
        return HttpResponse("<h1>Page Not Found</h1>")
    elif not adopter.acknowledged_faq:
        return render(request, "adopter/decision.html", context)

    today = datetime.date.today()

    return redirect("calendar_date", today.year, today.month, today.day)


@authenticated_user
@allowed_users(allowed_roles={'adopter'})
def acknowledged_faq(request):
    adopter = request.user.adopter
    adopter.acknowledged_faq = True
    adopter.save()

    return redirect('adopter_home')


def get_feed_of_shelterluv_people():
    global api_root
    headers = {'X-Api-Key': os.environ.get('SHELTERLUV_API_KEY')}
    request_address = '{0}people'.format(api_root)
    people_request = requests.get(request_address, headers=headers).json()
    people = people_request['people']

    print(people)

    return people


def clean_feed_of_shelterluv_people(people):
    clean_people = {}
    last_id = adopter_upload_settings.last_adopter_id_uploaded

    for person in people:
        id = person['Internal-ID']
        if int(id) > last_id:
            clean_people[id] = {
                'ID': person['Internal-ID'],
                'Firstname': person['Firstname'].title(),
                'Lastname': person['Lastname'].title(),
                'Email': person['Email'].lower(),
                'City': person['City'].title(),
                'State': person['State'],
                'Phone': person['Phone'][2:],
            }

    return clean_people


def date_delta(days):
    today = datetime.date.today()
    date_delta = today - datetime.timedelta(days=days)

    return date_delta


def stage_import(request):
    last_4_days = [date_delta(x) for x in range(4)]
    people = get_feed_of_shelterluv_people()
    people = clean_feed_of_shelterluv_people(people)

    if request.method == "POST":
        form_data = dict(request.POST)
        del form_data['csrfmiddlewaretoken']

        for id in form_data:
            if form_data[id][0] == 'on':
                person = people[id]
                email_for_search = person['Email']

                try:
                    user = User.objects.get(username=email_for_search)
                    adopter = Adopter.objects.get(
                        primary_email=email_for_search)
                    accepted_last_4_days = adopter.accept_date in last_4_days

                    if not accepted_last_4_days:
                        adopter = create_invite_email(adopter)
                except User.DoesNotExist:
                    adopter = create_adopter_from_api_import(person)
                    create_new_user_from_adopter(adopter)
                    create_invite_email(adopter)
                except:
                    pass

        if not sandbox:
            first_form_data_key = list(form_data.keys())[0]
            adopter_upload_settings.last_adopter_id_uploaded = int(first_form_data_key)
            adopter_upload_settings.save()

        return redirect('outbox')

    context = {
        'people': people
    }

    return render(request, "adopter/stage_upload.html", context)


def create_adopter_from_api_import(person_dict):
    auth_code = generate_auth_code()
    status = "1"

    new_adopter = Adopter.objects.create(
        auth_code = auth_code,
        city = person_dict['City'],
        f_name = person_dict['Firstname'],
        l_name = person_dict['Lastname'],
        out_of_state = False if person_dict['Phone'] == "NC" else True,
        phone_number = person_dict['Phone'],
        primary_email = person_dict['Email'],
        state = person_dict['State'],
        status = status
    )

    return new_adopter


def update_app_details_from_row(adopter_id, row):
    primary_email, secondary_email = get_email_from_row(row)

    new_adopter = Adopter.objects.update_or_create(
        pk=adopter_id, 
        defaults={
            'activity_level': row[32],
            'app_interest': row[11],
            'application_id': row[0],
            'has_fence': True if row[45] == "Yes" else False,
            'housing': row[35],
            'housing_type': row[33],
            'lives_with_parents': True if row[35] == "Live with Parents" else False,
            'out_of_state': False if row[19] == "NC" else True,
            'phone_number': row[22],
            'secondary_email': secondary_email,
            'state': row[19],
        }
    )

    return new_adopter

