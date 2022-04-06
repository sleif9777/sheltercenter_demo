from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Adopter
from appt_calendar.models import Appointment
from .forms import *
from schedule_template.models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate, SystemSettings
import datetime, time, csv, os
from random import randint
from emails.email_template import *
from email_mgr.models import EmailTemplate
from email_mgr.dictionary import *
from email_mgr.email_sender import *
from .adopter_manager import *
from django.contrib.auth.models import Group, User

system_settings = SystemSettings.objects.get(pk=1)

# Create your views here.

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
                    existing_adopter = Adopter.objects.get(adopter_email = "sheltercenterdev+" + clean_name(row[13]).replace(" ", "") + clean_name(row[14]).replace(" ", "") + "@gmail.com")
                    if existing_adopter.status == "2":
                        errors += [existing_adopter.adopter_full_name()]
                    elif existing_adopter.accept_date < (today - datetime.timedelta(days = 365)):
                        existing_adopter.accept_date = datetime.date.today()
                        existing_adopter.save()

                        if existing_adopter.out_of_state == True:
                            invite_oos_etemp(existing_adopter)
                        else:
                            invite(existing_adopter)
                    elif existing_adopter.accept_date not in [today - datetime.timedelta(days = x) for x in range(2)]:
                        duplicate_app(existing_adopter)
                except:
                    if row[13].islower() or row[13].isupper():
                        row[13] = clean_name(row[13])

                    if row[14].islower() or row[14].isupper():
                        row[14] = clean_name(row[14])

                    new_adopter.adopter_first_name = row[13]
                    new_adopter.adopter_last_name = row[14]
                    new_adopter.app_interest = row[11]

                    if str(os.environ.get('SANDBOX')) == "1":
                        print("sandbox")
                        new_adopter.adopter_email = "sheltercenterdev+" + new_adopter.adopter_first_name.replace(" ", "") + new_adopter.adopter_last_name.replace(" ", "") + "@gmail.com"
                    else:
                        print("prod")
                        new_adopter.adopter_email = "sheltercenterdev+" + new_adopter.adopter_first_name.replace(" ", "") + new_adopter.adopter_last_name.replace(" ", "") + "@gmail.com"
                        # new_adopter.adopter_email = row[28]
                        # new_adopter.secondary_email = row[29]

                    if row[35] == "Live with Parents":
                        new_adopter.lives_with_parents = True

                    if row[19] not in ["NC", "SC", "VA"]:
                        new_adopter.out_of_state = True

                    auth_code = randint(100000, 999999)

                    while auth_code % 100 == 0:
                        auth_code = randint(100000, 999999)

                    new_adopter.auth_code = auth_code

                    new_user = User.objects.create_user(username=new_adopter.adopter_email, email=new_adopter.adopter_email, password=str(auth_code))

                    new_adopter.user = new_user

                    g.user_set.add(new_user)

                    new_adopter.save()

                    if new_adopter.out_of_state == True:
                        invite_oos_etemp(new_adopter)
                    else:
                        invite(new_adopter)

            system_settings.last_adopter_upload = today
            system_settings.save()

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

                print(auth_code)

                adopter.auth_code = auth_code

                adopter.save()

                print(adopter.auth_code)

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
            else:
                print("blocked")

            form = AdopterForm()

    context = {
        'form': form,
        'dows': all_dows,
        'today': today,
        'role': 'admin',
    }

    return render(request, "adopter/addadopterform.html", context)

def login(request):
    adopters = Adopter.objects.all()

    context = {
        'adopters': adopters
    }

    return render(request, "adopter/login.html", context)

def manage(request):
    adopters = Adopter.objects.all()

    context = {
        'adopters': adopters,
        'role': 'admin'
    }

    return render(request, "adopter/adoptermgmt.html", context)

def edit_adopter(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)
    form = AdopterForm(request.POST or None, instance=adopter)

    try:
        current_appt = Appointment.objects.filter(adopter_choice=adopter).latest('id')
        current_appt_str = current_appt.date_and_time_string()
    except:
        current_appt = None
        current_appt_str = None

    if form.is_valid():
        form.save()
        return redirect('adopter_manage')
    else:
        form = AdopterForm(request.POST or None, instance=adopter)

    source = 'mgmt_' + str(adopter.id)

    print(source)

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

def faq(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)

    context = {
        'adopter': adopter,

    }

    return render(request, "adopter/faq.html", context)

def visitor_instructions(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)

    context = {
        'adopter': adopter,
        'role': 'adopter'
    }

    return render(request, "adopter/visitor_instructions.html", context)

def contact(request, adopter_id):
    all_dows = Daily_Schedule.objects
    form = ContactUsForm(request.POST or None)
    if form.is_valid():
        data = form.cleaned_data
        adopter = Adopter.objects.get(pk=adopter_id)
        message = data['message']
        new_contact_us_msg(adopter, message)
        return redirect('adopter_home', adopter_id)

    context = {
        'form': form,
        'all_dows': all_dows,
        'adopter': Adopter.objects.get(pk=adopter_id),
        'role': 'adopter'
    }

    return render(request, "adopter/contactteam.html", context)

def contact_adopter(request, appt_id, date_year, date_month, date_day, source):
    all_dows = Daily_Schedule.objects
    today = datetime.date.today()
    appt = Appointment.objects.get(pk=appt_id)

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

    template = replacer(template.text, adopter, appt)

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

            return redirect('chosen_board', 'admin')

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

            return redirect('calendar_date', "admin", date_year, date_month, date_day)

        elif 'mgmt' in source:
            return redirect('edit_adopter', adopter.id)

        elif 'add_form' in source:
            return redirect('add_adopter')

    context = {
        'form': form,
        'dows': all_dows,
        'today': today,
        'role': 'admin',
        'appt': appt
    }

    return render(request, "adopter/contactadopter.html", context)

def home_page(request):

    form = AdopterLoginField(request.POST or None)

    if form.is_valid():
        try:
            data = form.cleaned_data
            adopter = Adopter.objects.get(adopter_email=data['email'])

            print(adopter)

            return redirect('adopter_home', adopter.id)
        except:
            print('nope')

            return redirect('home_page')

    context = {
        'form': AdopterLoginField
    }

    return render(request, 'adopter/index.html', context)

def home(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)

    context = {
        'adopter': adopter,
        'full_name': full_name(adopter),
        'first_name': adopter.adopter_first_name,
        'role': 'adopter'
    }

    if adopter.status == "2":
        return HttpResponse("<h1>Page Not Found</h1>")
    elif adopter.acknowledged_faq == False:
        print(adopter.acknowledged_faq)
        print(context)
        return render(request, "adopter/decision.html", context)

    today = datetime.date.today()

    return redirect("adopter_calendar_date", "adopter", adopter.id, today.year, today.month, today.day)

def full_name(adopter_obj):
    return adopter_obj.adopter_first_name + " " + adopter_obj.adopter_last_name

def acknowledged_faq(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)

    Adopter.objects.filter(pk=adopter.id).update(acknowledged_faq = True)

    return redirect('adopter_home', adopter_id)
