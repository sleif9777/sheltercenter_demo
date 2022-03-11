from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Adopter
from appt_calendar.models import Appointment
from .forms import *
from schedule_template.models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate
import datetime, time, csv
from emails.email_template import *
from .adopter_manager import *


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
    }

    return render(request, "adopter/renderform.html", context)

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

    if request.method == 'POST' and request.FILES['app_file']:
        file = request.FILES['app_file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = list(csv.reader(decoded_file))
        print([today - datetime.timedelta(days = x) for x in range(2)])
        print(today - datetime.timedelta(days = 365))

        for row in reader[1:]:
            new_adopter = Adopter()

            try:
                existing_adopter = Adopter.objects.get(adopter_email = "sheltercenterdev+" + clean_name(row[13]).replace(" ", "") + clean_name(row[14]).replace(" ", "") + "@gmail.com")
                print("Adopter " + existing_adopter.adopter_full_name() + " already in system as adopter #" + str(existing_adopter.id))
                if existing_adopter.accept_date < (today - datetime.timedelta(days = 365)):
                    print("renewal")
                    existing_adopter.accept_date = datetime.date.today()
                    existing_adopter.save()

                    if existing_adopter.out_of_state == True:
                        invite_oos(existing_adopter)
                    elif existing_adopter.lives_with_parents == True:
                        invite_lives_w_parents(existing_adopter)
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

                new_adopter.save()

                if new_adopter.out_of_state == True:
                    invite_oos(new_adopter)
                elif new_adopter.lives_with_parents == True:
                    invite_lives_w_parents(new_adopter)
                else:
                    invite(new_adopter)

    elif form.is_valid():
        form.save()
        adopter = Adopter.objects.latest('id')

        #for testing purposes, do not put into prod
        adopter.adopter_email = "sheltercenterdev+" + adopter.adopter_first_name + adopter.adopter_last_name + "@gmail.com"
        adopter.save()

        if adopter.out_of_state == True:
            invite_oos(adopter)
        elif adopter.lives_with_parents == True:
            invite_lives_w_parents(adopter)
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

def contact_adopter(request, appt_id, date_year, date_month, date_day):
    all_dows = Daily_Schedule.objects
    today = datetime.date.today()
    appt = Appointment.objects.get(pk=appt_id)
    print(appt.adopter_choice)
    adopter = appt.adopter_choice
    print(adopter.adopter_first_name)
    form = ContactAdopterForm(request.POST or None)
    if form.is_valid():
        print("form!")
        data = form.cleaned_data
        message = data['message']
        include_links = data['include_links']
        new_contact_adopter_msg(adopter, message, include_links)
        return redirect('calendar_date', "admin", date_year, date_month, date_day)

    context = {
        'form': form,
        'dows': all_dows,
        'adopter_first_name': adopter.adopter_first_name,
        'today': today,
        'role': 'admin',
    }

    return render(request, "adopter/contactadopter.html", context)

def send_dogs_were_adopted_msg(request, appt_id):
    appt = Appointment.objects.get(pk=appt_id)
    adopter = appt.adopter_choice

    appt.comm_adopted_dogs = True
    appt.save()

    dogs_were_adopted(adopter, appt)

    return redirect('calendar', "admin")

def send_limited_matches_msg(request, appt_id, description, date_year, date_month, date_day):
    appt = Appointment.objects.get(pk=appt_id)
    adopter = appt.adopter_choice

    if description == "puppies":
        appt.comm_limited_puppies = True
    elif description == "small dogs":
        appt.comm_limited_small = True
    elif description == "lowshed":
        appt.comm_limited_hypo = True
        print("hypo")
    else:
        appt.comm_limited_other = True
        print("other")

    appt.save()

    limited_matches(adopter, appt, description)

    return redirect('calendar_date', "admin", date_year, date_month, date_day)

def home(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)

    context = {
        'adopter': adopter,
        'full_name': full_name(adopter),
        'first_name': adopter.adopter_first_name,
    }

    if adopter.acknowledged_faq == False:
        return render(request, "adopter/decision.html", context)

    today = datetime.date.today()

    return redirect("adopter_calendar_date", "adopter", adopter.id, today.year, today.month, today.day)

def full_name(adopter_obj):
    return adopter_obj.adopter_first_name + " " + adopter_obj.adopter_last_name

def acknowledged_faq(request, adopter_id):
    adopter = Adopter.objects.get(pk=adopter_id)

    Adopter.objects.filter(pk=adopter.id).update(acknowledged_faq = True)

    return redirect('adopter_home', adopter_id)
