from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Adopter
from appt_calendar.models import Appointment
from .forms import *
from schedule_template.models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate, SystemSettings
import datetime, time, csv, os
from random import randint
from email_mgr.models import EmailTemplate
from email_mgr.dictionary import *
from email_mgr.email_sender import *
from .adopter_manager import *
from visit_and_faq.models import *
from django.contrib.auth.models import Group, User
from dashboard.decorators import *

system_settings = SystemSettings.objects.get(pk=1)

# Create your views here.

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def add(request):
    all_dows = Daily_Schedule.objects
    today = datetime.date.today()
    form = AdopterForm(request.POST or None)
    g = Group.objects.get(name='adopter')

    try:
        if request.method == 'POST' and request.FILES['app_file']:
            file = request.FILES['app_file']
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = list(csv.reader(decoded_file))
            errors = []

            for row in reader[1:]:
                new_adopter = Adopter()

                try:
                    existing_user = User.objects.get(username = "sheltercenterdev+" + row[13].replace(" ", "").lower() + row[14].replace(" ", "").lower() + "@gmail.com")
                    existing_adopter = Adopter.objects.get(user=existing_user)
                    print(existing_adopter)
                    try:
                        if existing_adopter.status == "1":
                            print('miss1')
                            if existing_adopter.accept_date < (today - datetime.timedelta(days = 365)):
                                existing_adopter.accept_date = datetime.date.today()
                                existing_adopter.save()

                                if existing_adopter.out_of_state == True:
                                    invite_oos_etemp(existing_adopter)
                                else:
                                    invite(existing_adopter)
                            elif existing_adopter.accept_date not in [today - datetime.timedelta(days = x) for x in range(2)]:
                                duplicate_app(existing_adopter)
                        elif existing_adopter.status == "2":
                            print('miss2')
                            errors += [existing_adopter.adopter_full_name()]
                        elif existing_adopter.status == "3" and row[4] == "Accepted":
                            print('hit')
                            existing_adopter.status = "1"
                            existing_adopter.save()

                            if existing_adopter.out_of_state == True:
                                invite_oos_etemp(existing_adopter)
                            else:
                                invite(existing_adopter)
                    except:
                        pass
                except:
                    if row[13].islower() or row[13].isupper():
                        row[13] = clean_name(row[13])

                    if row[14].islower() or row[14].isupper():
                        row[14] = clean_name(row[14])

                    new_adopter.adopter_first_name = row[13]
                    new_adopter.adopter_last_name = row[14]
                    new_adopter.app_interest = row[11]

                    if str(os.environ.get('SANDBOX')) == "1":
                        new_adopter.adopter_email = "sheltercenterdev+" + new_adopter.adopter_first_name.replace(" ", "").lower() + new_adopter.adopter_last_name.replace(" ", "").lower() + "@gmail.com"
                    else:
                        new_adopter.adopter_email = row[28].lower()
                        new_adopter.secondary_email = row[29].lower()

                    if row[35] == "Live with Parents":
                        new_adopter.lives_with_parents = True

                    if row[19] not in ["NC", "SC", "VA"]:
                        new_adopter.out_of_state = True

                    auth_code = randint(100000, 999999)

                    while auth_code % 100 == 0:
                        auth_code = randint(100000, 999999)

                    new_adopter.auth_code = auth_code

                    new_user = User.objects.create_user(username=new_adopter.adopter_email.lower(), email=new_adopter.adopter_email, password=str(auth_code))

                    new_adopter.user = new_user

                    g.user_set.add(new_user)

                    if row[4] == "Denied":
                        new_adopter.status = "2"
                        errors += [new_adopter.adopter_full_name()]
                    elif row[4] == "Pending":
                        new_adopter.status = "3"
                        errors += [new_adopter.adopter_full_name()]

                    new_adopter.save()

                    if str(os.environ.get('SANDBOX')) != "1":
                        if row[4] == "Accepted":
                            if new_adopter.out_of_state == True:
                                invite_oos_etemp(new_adopter)
                            else:
                                invite(new_adopter)

            system_settings.last_adopter_upload = today
            system_settings.save()

            if errors != []:
                upload_errors(errors)
    except:
        if form.is_valid():
            form.save()
            adopter = Adopter.objects.latest('id')

            #for testing purposes, do not put into prod
            adopter.adopter_email = "sheltercenterdev+" + adopter.adopter_first_name + adopter.adopter_last_name + "@gmail.com"
            adopter.save()

            if adopter.status != "2":
                auth_code = randint(100000, 999999)

                while auth_code % 10 == 0:
                    auth_code = randint(100000, 999999)

                adopter.auth_code = auth_code

                new_user = User.objects.create_user(username=adopter.adopter_email.lower(), email=adopter.adopter_email, password=str(auth_code))

                adopter.user = new_user

                g.user_set.add(new_user)

                adopter.save()

                if adopter.out_of_state == True:
                    invite_oos_etemp(adopter)
                elif adopter.adopting_foster or adopter.friend_of_foster or adopter.adopting_host:
                    shellappt = Appointment()
                    shellappt.time = datetime.datetime.now()
                    shellappt.adopter_choice = adopter
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

            form = AdopterForm()

    context = {
        'form': form,
        'dows': all_dows,
        'today': today,
        'role': 'admin',
    }

    return render(request, "adopter/addadopterform.html", context)

@authenticated_user
@allowed_users(allowed_roles={'superuser'})
def login(request):
    adopters = Adopter.objects.all()

    context = {
        'adopters': adopters
    }

    return render(request, "adopter/login.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def manage(request):
    adopters = Adopter.objects.all()

    context = {
        'adopters': adopters,
        'role': 'admin'
    }

    return render(request, "adopter/adoptermgmt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def send_to_inactive(request):
    add_date = datetime.date.today() - datetime.timedelta(days = 5)
    adopters = Adopter.objects.filter(accept_date=add_date, acknowledged_faq=False)

    for adopter in adopters:
        inactive_invite(adopter)

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
    }

    return render(request, "adopter/set_alert_date.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin'})
def edit_adopter(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)
    form = AdopterForm(request.POST or None, instance=adopter)

    adopter_curr_status = adopter.status[:]

    try:
        current_appt = Appointment.objects.filter(adopter_choice=adopter).latest('id')
        current_appt_str = current_appt.date_and_time_string()
    except:
        current_appt = None
        current_appt_str = None

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
        'appt_str': current_appt_str,
        'role': 'admin',
        'schedulable': ["1", "2", "3"],
        'source': source
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
    }

    return render(request, "adopter/faq_test_harness.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'adopter'})
def visitor_instructions(request):
    all_instrs = VisitorInstruction.objects.all()

    context = {
        'all_instrs': all_instrs
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
        adopter = appt.adopter_choice
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
                appt.outcome = "6"

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
        'appt': appt
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
        'full_name': full_name(adopter),
        'first_name': adopter.adopter_first_name,
        'role': 'adopter',
        'faq_dict': faq_dict,
    }

    if adopter.status == "2":
        return HttpResponse("<h1>Page Not Found</h1>")
    elif adopter.acknowledged_faq == False:
        return render(request, "adopter/decision.html", context)

    today = datetime.date.today()

    return redirect("calendar_date", today.year, today.month, today.day)

def full_name(adopter_obj):
    return adopter_obj.adopter_first_name + " " + adopter_obj.adopter_last_name

@authenticated_user
@allowed_users(allowed_roles={'adopter'})
def acknowledged_faq(request):
    adopter = request.user.adopter

    Adopter.objects.filter(pk=adopter.id).update(acknowledged_faq = True)

    return redirect('adopter_home')
