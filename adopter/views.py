from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Adopter
from appt_calendar.models import Appointment
from .forms import *
from schedule_template.models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate
import datetime, time
from emails.email_template import *


# Create your views here.
def login(request):
    adopters = Adopter.objects.all()

    context = {
        'adopters': adopters
    }

    return render(request, "adopter/login.html", context)

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
    if form.is_valid():
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

            adopter.has_current_appt = False

            invite_foster_adoption(adopter)
        elif adopter.friend_of_foster == True:
            shellappt = Appointment()
            shellappt.time = datetime.datetime.now()
            shellappt.adopter_choice = adopter
            shellappt.dog = adopter.chosen_dog
            shellappt.outcome = "3"

            adopter.has_current_appt = False

            invite_friends_of_foster_adoption(adopter)
        elif adopter.adopting_host == True:
            shellappt = Appointment()
            shellappt.time = datetime.datetime.now()
            shellappt.adopter_choice = adopter
            shellappt.dog = adopter.chosen_dog
            shellappt.outcome = "3"

            adopter.has_current_appt = False

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
    dogs_were_adopted(adopter, appt)

    return redirect('calendar', "admin")

def send_limited_matches_msg(request, appt_id, description, date_year, date_month, date_day):
    print("yes!")
    appt = Appointment.objects.get(pk=appt_id)
    adopter = appt.adopter_choice
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
