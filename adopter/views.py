from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Adopter
from appt_calendar.models import Appointment
from .forms import *
from schedule_template.models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate, SystemSettings
import datetime, time, csv, os, sys
from random import randint
from email_mgr.models import *
from email_mgr.dictionary import *
from email_mgr.email_sender import *
from .adopter_manager import *
from visit_and_faq.models import *
from django.contrib.auth.models import Group, User
from dashboard.decorators import *

system_settings = SystemSettings.objects.get(pk=1)

# Create your views here.

def create_adopter_from_row(row):
    #initiate adopter object
    new_adopter = Adopter()

    #clean and set name
    if row[13].islower() or row[13].isupper():
        row[13] = row[13].title()

    if row[14].islower() or row[14].isupper():
        row[14] = row[14].title()

    new_adopter.f_name = row[13]
    new_adopter.l_name = row[14]

    #add application detais
    new_adopter.city = row[18].title()
    new_adopter.state = row[19]
    new_adopter.housing_type = row[33]
    new_adopter.housing = row[35]
    new_adopter.activity_level = row[32]
    new_adopter.has_fence = True if row[45] == "Yes" else False
    new_adopter.app_interest = row[11]

    #application id
    new_adopter.application_id = row[0]

    #if in sandbox assign shell email
    if str(os.environ.get('SANDBOX')) == "1":
        new_adopter.primary_email = "sheltercenterdev+" + new_adopter.f_name.replace(" ", "").lower() + new_adopter.l_name.replace(" ", "").lower() + "@gmail.com"
    #else use real email
    else:
        new_adopter.primary_email = row[28].lower()
        new_adopter.secondary_email = row[29].lower()

    #set lives with parents attribute
    if row[35] == "Live with Parents":
        new_adopter.lives_with_parents = True

    #set out of state
    if row[19] not in ["NC", "SC", "VA"]:
        new_adopter.out_of_state = True

    #set an auth code that isn't divisible by 100
    auth_code = randint(100000, 999999)

    while auth_code % 100 == 0:
        auth_code = randint(100000, 999999)

    new_adopter.auth_code = auth_code

    #set status
    if row[4] == "Denied":
        new_adopter.status = "2"
    elif row[4] == "Pending":
        new_adopter.status = "3"

    new_adopter.save()

    return new_adopter

def create_new_user_from_adopter(adopter):
    adopter_group = Group.objects.get(name='adopter')

    #initiate user object
    new_user = User.objects.create_user(username=adopter.primary_email.lower(), email=adopter.primary_email, password=str(adopter.auth_code))

    #assign to adopter and save
    adopter.user = new_user
    adopter.save()

    adopter_group.user_set.add(new_user)

#can be refactored for genericity
def create_invite_inactive_email(adopter):
    message = PendingMessage()

    message.subject = "Are you ready to schedule your appointment?"
    message.email = adopter.primary_email

    template = EmailTemplate.objects.get(template_name="Are you ready to schedule your appointment?")

    html = replacer(template.text, adopter, None)
    text = strip_tags(html, adopter, None)

    message.html = html
    message.text = text

    message.save()

#can be refactored for genericity
def create_invite_email(adopter):
    message = PendingMessage()

    message.subject = "Your adoption request has been reviewed: " + adopter.full_name().upper()
    message.email = adopter.primary_email

    if adopter.out_of_state == True:
        template = EmailTemplate.objects.get(template_name="Add Adopter (outside NC, VA, SC)")
    else:
        template = EmailTemplate.objects.get(template_name="Add Adopter (inside NC, VA, SC)")

    html = replacer(template.text, adopter, None)
    text = strip_tags(html, adopter, None)

    message.html = html
    message.text = text

    message.save()

def handle_existing(existing_adopter):
    today = datetime.date.today()

    #if the adopter is approved...
    if existing_adopter.status == "1":
        #...and was accepted over a year ago, send new invite
        if existing_adopter.accept_date < (today - datetime.timedelta(days = 365)):
            existing_adopter.accept_date = datetime.date.today()
            existing_adopter.save()
            create_invite_email(existing_adopter)
        #...and was accepted under a year ago, but more than two days ago, send push
        elif existing_adopter.accept_date not in [today - datetime.timedelta(days = x) for x in range(2)] and not (adopter.adopting_foster or adopter.friend_of_foster or adopter.adopting_host):
                duplicate_app(existing_adopter)

    #if moved from pending to approved, send invite
    elif existing_adopter.status == "3" and row[4] == "Accepted":
        existing_adopter.status = "1"
        existing_adopter.save()
        create_invite_email(existing_adopter)

def add_from_file(file):
    errors = []

    decoded_file = file.read().decode('utf-8').splitlines()
    reader = list(csv.reader(decoded_file))
    errors = []

    for row in reader[1:]:
        try:
            try:
                existing_user = User.objects.get(username = "sheltercenterdev+" + row[13].replace(" ", "").lower() + row[14].replace(" ", "").lower() + "@gmail.com")
                existing_adopter = Adopter.objects.get(user=existing_user)
            except:
                existing_adopter = Adopter.objects.filter(primary_email="sheltercenterdev+" + row[13].replace(" ", "").lower() + row[14].replace(" ", "").lower() + "@gmail.com").latest('id')

            #update to newest application
            existing_adopter.application_id = row[0]
            existing_adopter.save()

            #if blocked, add to error report
            if existing_adopter.status == "2":
                errors += [existing_adopter]

            #else handle message
            else:
                handle_existing(existing_adopter)
        except Exception as f:
            print('f', f)
            adopter = create_adopter_from_row(row)

            if adopter.status == "1":
                #create Application
                create_new_user_from_adopter(adopter)
                create_invite_email(adopter)
            else:
                errors += [adopter]

    system_settings.last_adopter_upload = datetime.date.today()
    system_settings.save()

    if errors != []:
        upload_errors(errors)

    return redirect('outbox')

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def add_from_form(adopter):
    #for testing purposes, do not put into prod
    if str(os.environ.get('SANDBOX')) == "1":
        adopter.primary_email = "sheltercenterdev+" + adopter.f_name.replace(" ", "").lower() + adopter.l_name.replace(" ", "").lower() + "@gmail.com"
    #else use real email
    else:
        adopter.primary_email = row[28].lower()
        adopter.secondary_email = row[29].lower()

    #set an auth code that isn't divisible by 100
    auth_code = randint(100000, 999999)

    while auth_code % 100 == 0:
        auth_code = randint(100000, 999999)

    adopter.auth_code = auth_code

    adopter.save()

    if adopter.status == "1":
        create_new_user_from_adopter(adopter)

        if adopter.out_of_state == True:
            invite_oos_etemp(adopter)
        elif adopter.adopting_foster or adopter.friend_of_foster or adopter.adopting_host:
            shellappt = Appointment()
            shellappt.time = datetime.datetime.now()
            shellappt.adopter = adopter
            shellappt.dog = adopter.chosen_dog
            shellappt.outcome = "3"

            shellappt.save()

            adopter.has_current_appt = False
            adopter.acknowledged_faq = True
            adopter.save()

            if adopter.adopting_foster:
                return redirect('contact_adopter', shellappt.id, shellappt.date.year, shellappt.date.month, shellappt.date.day, 'add_form_adopting_foster')
            elif adopter.friend_of_foster:
                return redirect('contact_adopter', shellappt.id, shellappt.date.year, shellappt.date.month, shellappt.date.day, 'add_form_friend_of_foster')
            else:
                return redirect('contact_adopter', shellappt.id, shellappt.date.year, shellappt.date.month, shellappt.date.day, 'add_form_adopting_host')
        elif adopter.carryover_shelterluv:
            carryover_temp(adopter)
        else:
            invite(adopter)

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def add(request):
    today = datetime.date.today()
    form = AdopterForm(request.POST or None)
    adopter_group = Group.objects.get(name='adopter')

    #try adding from file
    try:
        if request.method == 'POST' and request.FILES['app_file']:
            file = request.FILES['app_file']
            add_from_file(file)
    #except no file, add manually without application
    except Exception as g:
        print('g', g)
        if form.is_valid():
            form.save()
            adopter = Adopter.objects.latest('id')
            add_from_form(adopter)

    form = AdopterForm()

    context = {
    'form': form,
    'today': today,
    'role': 'admin',
    'page_title': "Add Adopters",
    }

    return render(request, "adopter/addadopterform.html", context)

@authenticated_user
@allowed_users(allowed_roles={'superuser'})
def login(request):
    adopters = Adopter.objects.all()

    context = {
        'adopters': adopters,
        'page_title': "Log In",
    }

    return render(request, "adopter/login.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def manage(request):
    adopters = Adopter.objects.all()
    alphabet = [chr(x) for x in range(65, 91)]
    digits = [chr(x) for x in range(48, 58)]

    context = {
        'adopters': adopters,
        'role': 'admin',
        'alphabet': alphabet,
        'digits': digits,
        'lname_fname': False,
        'page_title': "Manage Adopters",
    }

    return render(request, "adopter/adoptermgmt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def manage_filter(request, filter, char):
    if filter == 'fname':
        adopters = Adopter.objects.filter(f_name__startswith=char)
        lname_fname = False
    elif filter == 'lname':
        adopters = Adopter.objects.filter(l_name__startswith=char).order_by('l_name')
        lname_fname = True
    elif filter == "email":
        char = char.lower()
        adopters = Adopter.objects.filter(primary_email__startswith=char)
        lname_fname = False

    alphabet = [chr(x) for x in range(65, 91)]
    digits = [chr(x) for x in range(48, 58)]

    context = {
        'adopters': adopters,
        'role': 'admin',
        'alphabet': alphabet,
        'digits': digits,
        'lname_fname': lname_fname,
        'page_title': "Manage Adopters",
    }

    return render(request, "adopter/adoptermgmt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def send_to_inactive(request):
    add_date = datetime.date.today() - datetime.timedelta(days = 5)
    adopters = Adopter.objects.filter(accept_date=add_date, acknowledged_faq=False, status="1")

    for adopter in adopters:
        create_invite_inactive_email(adopter)

    return redirect('adopter_manage')

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def resend_invite(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)

    invite(adopter)

    return redirect('adopter_manage')

@authenticated_user
@allowed_users(allowed_roles={'admin'})
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

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def edit_adopter(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)
    form = AdopterForm(request.POST or None, instance=adopter)

    adopter_curr_status = adopter.status[:]

    try:
        current_appt = Appointment.objects.filter(adopter=adopter).latest('id')
        current_appt_str = current_appt.date_and_time_string()
        date = current_appt.date
    except:
        current_appt = None
        current_appt_str = None
        date = None

    if form.is_valid():
        form.save()

        if adopter.status != adopter_curr_status and adopter.status == "1":
            if adopter.out_of_state == True:
                invite_oos_etemp(adopter)
            else:
                invite(adopter)

        return redirect('adopter_manage')
    else:
        form = AdopterForm(request.POST or None, instance=adopter)

    source = 'mgmt_' + str(adopter.id)

    context = {
        'form': form,
        'adopter': adopter,
        'appt': current_appt,
        'date': date,
        'appt_str': current_appt_str,
        'schedulable': ["1", "2", "3"],
        'source': source,
        'show_timestr': True,
        'today': datetime.date.today(),
        'page_title': "Edit Adopter"
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
def contact(request):
    all_dows = Daily_Schedule.objects
    form = ContactUsForm(request.POST or None)
    if form.is_valid():
        data = form.cleaned_data
        adopter = request.user.adopter
        message = data['message']
        new_contact_us_msg(adopter, message)
        return redirect('adopter_home')

    context = {
        'form': form,
        'all_dows': all_dows,
        'page_title': "Contact Us",
    }

    return render(request, "adopter/contactteam.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def contact_adopter(request, appt_id, date_year, date_month, date_day, source):
    today = datetime.date.today()
    try:
        appt = Appointment.objects.get(pk=appt_id)
    except:
        appt = None

    if 'mgmt' not in source:
        adopter = appt.adopter
    else:
        adopter_id = source.split('_')[1]
        adopter = Adopter.objects.get(pk=adopter_id)

    if source in ["calendar", "update"] or 'mgmt' in source:
        template = EmailTemplate.objects.get(template_name="Contact Adopter")
    elif source == "ready_positive":
        template = EmailTemplate.objects.get(template_name="Ready to Roll (Heartworm Positive)")
    elif source == "ready_negative":
        template = EmailTemplate.objects.get(template_name="Ready to Roll (Heartworm Negative)")
    elif source == "limited_puppies":
        template = EmailTemplate.objects.get(template_name="Limited Puppies")
    elif source == "limited_small":
        template = EmailTemplate.objects.get(template_name="Limited Small Dogs")
    elif source == "limited_small_puppies":
        template = EmailTemplate.objects.get(template_name="Limited Small Breed Puppies")
    elif source == "limited_hypo":
        template = EmailTemplate.objects.get(template_name="Limited Hypo")
    elif source == 'dogs_were_adopted':
        template = EmailTemplate.objects.get(template_name="Dogs Were Adopted")
    elif source == 'add_form_adopting_foster':
        template = EmailTemplate.objects.get(template_name="Add Adopter (Adopting Foster)")
    elif source == 'add_form_friend_of_foster':
        template = EmailTemplate.objects.get(template_name="Add Adopter (Friend of Foster)")
    elif source == 'add_form_adopting_host':
        template = EmailTemplate.objects.get(template_name="Add Adopter (Host Weekend)")

    try:
        template = replacer(template.text.replace('*SIGNATURE*', request.user.profile.signature), adopter, appt)
    except:
        base_user = User.objects.get(username="base")
        template = replacer(template.text.replace('*SIGNATURE*', base_user.profile.signature), adopter, appt)

    form = ContactAdopterForm(request.POST or None, initial={'message': template})

    if form.is_valid():
        data = form.cleaned_data
        message = data['message']
        new_contact_adopter_msg(adopter, message)

        if source in ["update", "ready_positive", "ready_negative"]:

            appt.last_update_sent = today

            if source in ['ready_positive', 'ready_negative']:
                appt.outcome = "7"

            if source == 'ready_positive':
                appt.heartworm = True

            appt.save()

            return redirect('chosen_board')

        elif source in ['limited_puppies', 'limited_small', 'limited_hypo', 'limited_small_puppies', 'dogs_were_adopted', 'calendar']:

            if source == "limited_puppies":
                appt.comm_limited_puppies = True
            elif source == "limited_small":
                appt.comm_limited_small = True
            elif source == "limited_hypo":
                appt.comm_limited_hypo = True
            elif source == "limited_small_puppies":
                appt.comm_limited_small_puppies = True
            elif source == "dogs_were_adopted":
                appt.comm_adopted_dogs = True

            appt.save()

            return redirect('calendar_date', date_year, date_month, date_day)

        elif 'mgmt' in source:
            return redirect('edit_adopter', adopter.id)

        elif 'add_form' in source:
            return redirect('add_adopter')

    context = {
        'form': form,
        'appt': appt,
        'page_title': "Contact {0}".format(adopter.full_name()),
    }

    return render(request, "adopter/contactadopter.html", context)

def home_page(request):
    return redirect('login')

@authenticated_user
@allowed_users(allowed_roles={'adopter'})
def home(request):
    adopter = request.user.adopter

    faq_dict = {}

    for sec in FAQSection.objects.all().iterator():
        faq_dict[sec] = [q for q in sec.questions.iterator()]

    context = {
        'adopter': adopter,
        'full_name': adopter.full_name(),
        'first_name': adopter.f_name,
        'role': 'adopter',
        'faq_dict': faq_dict,
        'page_title': "Home",
    }

    if adopter.status == "2":
        return HttpResponse("<h1>Page Not Found</h1>")
    elif adopter.acknowledged_faq == False:
        return render(request, "adopter/decision.html", context)

    today = datetime.date.today()

    return redirect("calendar_date", today.year, today.month, today.day)

@authenticated_user
@allowed_users(allowed_roles={'adopter'})
def acknowledged_faq(request):
    adopter = request.user.adopter

    Adopter.objects.filter(pk=adopter.id).update(acknowledged_faq = True)

    return redirect('adopter_home')
