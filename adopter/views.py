from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Adopter
from appt_calendar.models import Appointment
from .forms import *
from schedule_template.models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate, SystemSettings
import datetime, time, csv
from random import randint
from emails.email_template import *
from email_mgr.models import EmailTemplate
from email_mgr.dictionary import *
from email_mgr.email_sender import *
from .adopter_manager import *

system_settings = SystemSettings.objects.get(pk=1)

# Create your views here.

def simple_add_form(request):

    return render(request, "adopter/simple_add_form.html")

def simple_add_form_submit(request):

    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']

    try:
        subjnotes = request.POST['subjnotes']
    except:
        subjnotes = None

    simple_invite(fname, lname, email, subjnotes)

    return redirect('simple_add_form')

def simple_add_form_oos(request):

    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    subjnotes = request.POST['subjnotes']

    simple_invite_oos(fname, lname, email, subjnotes)

    return redirect('simple_add_form')

def login(request):
    adopters = Adopter.objects.all()

    context = {
        'adopters': adopters
    }

    return render(request, "adopter/login.html", context)

def manage(request):
    adopters = Adopter.objects.all()

    context = {
        'adopters': adopters
    }

    return render(request, "adopter/adoptermgmt.html", context)

def edit_adopter(request, adopter_id):
#    dow_id -= 2
    adopter = Adopter.objects.get(pk=adopter_id)
    #form = GenericTimeslotModelForm(request.POST or None, initial={"day_of_week": dow.day_of_week})
    form = AdopterForm(request.POST or None, instance=adopter)
    if form.is_valid():
        form.save()
        return redirect('adopter_manage')
    else:
        form = AdopterForm(request.POST or None, instance=adopter)

    context = {
        'form': form,
        'adopter': adopter,
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

    }

    return render(request, "adopter/visitor_instructions.html", context)

def add(request):
    all_dows = Daily_Schedule.objects
    today = datetime.date.today()
    form = AdopterForm(request.POST or None)

    try:
        if request.method == 'POST' and request.FILES['app_file']:
            file = request.FILES['app_file']
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = list(csv.reader(decoded_file))
            print([today - datetime.timedelta(days = x) for x in range(2)])
            print(today - datetime.timedelta(days = 365))
            errors = []

            for row in reader[1:]:
                new_adopter = Adopter()

                try:
                    existing_adopter = Adopter.objects.get(adopter_email = "sheltercenterdev+" + clean_name(row[13]).replace(" ", "") + clean_name(row[14]).replace(" ", "") + "@gmail.com")
                    print("Adopter " + existing_adopter.adopter_full_name() + " already in system as adopter #" + str(existing_adopter.id))
                    if existing_adopter.status == "2":
                        print("blocked")
                        errors += [existing_adopter.adopter_full_name()]
                    elif existing_adopter.accept_date < (today - datetime.timedelta(days = 365)):
                        print("renewal")
                        existing_adopter.accept_date = datetime.date.today()
                        existing_adopter.save()

                        if existing_adopter.out_of_state == True:
                            invite_oos_etemp(existing_adopter)
                        else:
                            invite(existing_adopter)
                    elif existing_adopter.accept_date not in [today - datetime.timedelta(days = x) for x in range(2)]:
                        duplicate_app(existing_adopter)
                    else:
                        print("added today")
                except:
                    print("added now")
                    if row[13].islower() or row[13].isupper():
                        row[13] = clean_name(row[13])

                    if row[14].islower() or row[14].isupper():
                        row[14] = clean_name(row[14])
                    #
                    # print(row[3])
                    # print(type(row[3]))

                    new_adopter.adopter_first_name = row[13]
                    new_adopter.adopter_last_name = row[14]
                    new_adopter.app_interest = row[11]
                    new_adopter.adopter_email = "sheltercenterdev+" + new_adopter.adopter_first_name.replace(" ", "") + new_adopter.adopter_last_name.replace(" ", "") + "@gmail.com"
                    print(new_adopter.adopter_email)

                    if row[35] == "Live with Parents":
                        new_adopter.lives_with_parents = True

                    if row[19] not in ["NC", "SC", "VA"]:
                        new_adopter.out_of_state = True

                    auth_code = randint(100000, 999999)

                    while auth_code % 10 == 0:
                        auth_code = randint(100000, 999999)

                    print(row[13] + " " + row[14])
                    print(auth_code)

                    new_adopter.auth_code = auth_code

                    new_adopter.save()

                    print(new_adopter.auth_code)

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
                elif adopter.adopting_foster == True:
                    shellappt = Appointment()
                    shellappt.time = datetime.datetime.now()
                    shellappt.adopter_choice = adopter
                    shellappt.dog = adopter.chosen_dog
                    shellappt.outcome = "3"

                    shellappt.save()

                    adopter.has_current_appt = False

                    invite_foster_adoption(adopter)
                elif adopter.friend_of_foster == True:
                    shellappt = Appointment()
                    shellappt.time = datetime.datetime.now()
                    shellappt.adopter_choice = adopter
                    shellappt.dog = adopter.chosen_dog
                    shellappt.outcome = "3"

                    shellappt.save()

                    adopter.has_current_appt = False

                    adopter.save()

                    invite_friends_of_foster_adoption(adopter)
                elif adopter.adopting_host == True:
                    shellappt = Appointment()
                    shellappt.time = datetime.datetime.now()
                    shellappt.adopter_choice = adopter
                    shellappt.dog = adopter.chosen_dog
                    shellappt.outcome = "3"

                    shellappt.save()

                    adopter.has_current_appt = False

                    adopter.save()

                    invite_host_adoption(adopter)
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
        'adopter': Adopter.objects.get(pk=adopter_id)
    }

    return render(request, "adopter/contactteam.html", context)

def contact_adopter(request, appt_id, date_year, date_month, date_day, source):
    all_dows = Daily_Schedule.objects
    today = datetime.date.today()
    appt = Appointment.objects.get(pk=appt_id)
    adopter = appt.adopter_choice

    if source in ["calendar", "update"]:
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

    context = {
        'form': form,
        'dows': all_dows,
        'today': today,
        'role': 'admin',
        'appt': appt
    }

    return render(request, "adopter/contactadopter.html", context)

def home(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)

    context = {
        'adopter': adopter,
        'full_name': full_name(adopter),
        'first_name': adopter.adopter_first_name,
    }

    if adopter.status == "2":
        return HttpResponse("<h1>Page Not Found</h1>")
    elif adopter.acknowledged_faq == False:
        return render(request, "adopter/decision.html", context)

    today = datetime.date.today()

    return redirect("adopter_calendar_date", "adopter", adopter.id, today.year, today.month, today.day)

def full_name(adopter_obj):
    return adopter_obj.adopter_first_name + " " + adopter_obj.adopter_last_name

def acknowledged_faq(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)

    Adopter.objects.filter(pk=adopter.id).update(acknowledged_faq = True)

    return redirect('adopter_home', adopter_id)
