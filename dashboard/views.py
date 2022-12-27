import datetime
import json
import random
import requests
import time

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render 

from .decorators import *
from .models import *
from .forms import *
from .templatetags.wishlist_extras import *
from adopter.models import *
from appt_calendar.appointment_manager import *
from appt_calendar.date_time_strings import *
from appt_calendar.forms import *
from appt_calendar.models import *
from email_mgr.email_sender import *
from schedule_template.models import *
from wishlist.models import *
from wishlist.views import *

system_settings = SystemSettings.objects.get(pk=1)
today = datetime.date.today()

# AUTHENTICATION WORKFLOWS
@unauthenticated_user
def login_page(request):
    # render login page for all users (intended for adopters)
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            get_and_update_dogs()
            user_groups = get_groups(user)

            if 'adopter' in user_groups and not user.adopter.acknowledged_faq:
                return redirect('adopter_home')
            else:
                return redirect('calendar')

    context = {
        'cred_placeholder': 'adopter@sheltercenter.dog',
        'login_cred': 'email address',
        'other_login': '{% url "staff_login" %}',
        'other_role': 'Greeters and staff',
        'pw_cred': 'authorization code',
        'pw_placeholder': '123456 (This is in the email we sent you)',
        'page_title': "Log In",
    }

    return render(request, 'dashboard/login.html', context)


@unauthenticated_user
def staff_login(request):
    # renders login page for staff
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            user_groups = get_groups(user)
            login(request, user)
            return redirect('calendar')

    context = {
        'cred_placeholder': 'Username',
        'login_cred': 'username',
        'other_login': '{% url "login" %}',
        'other_role': 'Adopters',
        'pw_cred': 'password',
        'pw_placeholder': 'Password',
        'page_title': "Log In",
    }

    return render(request, 'dashboard/login.html', context)


@authenticated_user
def logout_user(request):
    # logs out user
    logout(request)
    return redirect('login')

# OTHER PAGES
# depracate?
@authenticated_user
@allowed_users(allowed_roles={'superuser'})
def images(request):
    return render(request, 'dashboard/images.html')


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_signature(request):
    # renders edit signature page for message substitution
    profile = Profile.objects.get(user=request.user)
    form = EmailSigForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('email_home')
    else:
        form = EmailSigForm(request.POST or None, instance=profile)

    context = {
        'form': form,
        'e_template': profile,
        'page_title': "Edit Signature",
    }

    return render(request, "email_mgr/add_template.html", context)


def fake500(request):
    # throws an error on purpose, testing purposes only
    return render(request, "dashboard/fake500.html")


def error_500(request):
    # customized error page
    all_available_dogs = get_all_available_dogs()
    display_dog = random.choice(all_available_dogs)
    display_dog_info = display_dog.info
    age_months = int(display_dog_info['Age'])
    dog_age = "Age {0}Y {1}M".format(age_months // 12, age_months % 12)
    dog_breed = display_dog_info['Breed']
    dog_img = display_dog_info['CoverPhoto']
    dog_name = display_dog_info['Name']
    dog_sex = display_dog_info['Sex']

    try:
        dog_weight = "{0} lbs., ".format(display_dog_info['CurrentWeightPounds'])
    except:
        dog_weight = ""

    context = {
        'dog_age': dog_age,
        'dog_breed': dog_breed,
        'dog_img': dog_img,
        'dog_name': dog_name,
        'dog_sex': dog_sex,
        'dog_weight': dog_weight,
    }

    return render(request, 'dashboard/500.html', context)


def user_settings(request):
    # renders the user settings page (adjust appointment card view)
    form = AppointmentCardPreferences(
        request.POST or None, 
        instance=request.user.profile
    )
    
    if form.is_valid():
        form.save()

    context = {'form': form}
    return render(request, 'dashboard/user_settings.html', context)


# CALENDAR GENERATION AND AUXILIARY FUNCTIONS
def generate_calendar(user, load, date_year, date_month, date_day):
    # master function, calls helper functions to piece together data, 
    # sets a few constants
    global today
    current_appt = gen_cal_get_current_appt(user)
    date = datetime.date(date_year, date_month, date_day)
    user_groups = get_groups(user)
    
    context = {
        'current_appt': current_appt,
        'date': date,
        'page_title': "Calendar",
        'popular_dogs': gen_cal_get_popular_dogs(),
    }

    announcements_dict = gen_cal_get_announcements_dict(date)
    dates_and_delta_dict = gen_cal_get_dates_and_delta_dict(date)
    offsite_dog_dict = gen_cal_get_offsite_dog_dict()
    short_notice_dict = gen_cal_get_short_notice_dict(date)
    timeslots_dict = gen_cal_get_timeslots_dict(date, load, user, user_groups)

    context.update(announcements_dict)
    context.update(dates_and_delta_dict)
    context.update(offsite_dog_dict)
    context.update(short_notice_dict)
    context.update(timeslots_dict)

    if 'admin' in user_groups:
        admin_info_dict = gen_cal_get_admin_info_dict()
        context.update(admin_info_dict)

    return context


def filter_timeslots_admin(timeslots_query, date, load):
    # filters appointments per timeslot and discards empty timeslots
    timeslots = {}
    for time in timeslots_query:
        match load:
            case "full":
                timeslots[time] = list(time.appointments.filter(
                    date=date,
                    time=time.time
                ))
            case "reschedule":
                timeslots[time] = list(time.appointments.filter(
                    adopter=None,
                    appt_type__in=["1", "2", "3"],
                    date=date, 
                    time=time.time, 
                ))

                if len(timeslots[time]) == 0:
                    timeslots.pop(time)

    return timeslots


def filter_timeslots_adopter(timeslots_query, date, adopter):
    # filters appointments per timeslot and discards empty timeslots,
    # accounts for and hides appointments within 2 hours
    timeslots = {}

    for time in timeslots_query:
        #calculate the timeslots datetime, the current time,
        #and the cutoff period (2 hours later)
        dt_time = datetime.datetime(
            time.date.year, time.date.month, time.date.day, 
            time.time.hour, time.time.minute)
        now = datetime.datetime.now()
        cutoff = now + datetime.timedelta(hours=2)

        #if past or less than two hours from now, show no appts
        if cutoff >= dt_time:
            timeslots[time] = []
        else:
            timeslots[time] = list(time.appointments.filter(
                appt_type__in=["1", "2", "3"],
                adopter__in=[adopter, None],
                date=date, 
                time=time.time, 
            ))

        #delete unnecessary timeslots
        if timeslots[time] == []:
            timeslots.pop(time)

    return timeslots


def gen_cal_get_admin_info_dict():
    # calculate empty dates and no outcome appts for staff views only
    empty_dates = get_empty_days()
    no_outcome_appts = get_no_outcome_appts()

    admin_info_dict = {
        'empty_dates': empty_dates,
        'no_outcome_appts': no_outcome_appts
    }

    return admin_info_dict


def gen_cal_get_announcements_dict(date):
    # try to get announcements or default to none
    try:
        calendar_announcement = CalendarAnnouncement.objects.get(pk=1)
    except:
        calendar_announcement = None
    
    try:
        daily_announcement = DailyAnnouncement.objects.get(date=date)
    except:
        daily_announcement = None

    try:
        internal_announcement = InternalAnnouncement.objects.get(date=date)
    except:
        internal_announcement = None

    announcements_dict = {
        'calendar_announcement': calendar_announcement,
        'daily_announcement': daily_announcement,
        'internal_announcement': internal_announcement,
    }

    return announcements_dict


def gen_cal_get_current_appt(user):
    # return the latest appointment by adopter or none
    try:
        return Appointment.objects.filter(adopter=user.adopter).latest('id')
    except:
        return None


def gen_cal_get_dates_and_delta_dict(date):
    # set up date constants and other date-related attributes
    global today

    date_pretty = date_str(date)
    delta_from_today = (date - datetime.date.today()).days
    next_day = date + datetime.timedelta(days=1)
    previous_day = date - datetime.timedelta(days=1)
    visible_to_adopters = True if delta_from_today <= 13 else False
    weekday = weekday_str(date)

    dates_delta_cal_dict = {
        'date_pretty': date_pretty,
        'delta': delta_from_today,
        'next_day': next_day,
        'previous_day': previous_day,
        'today': today,
        'visible': visible_to_adopters,
        'weekday': weekday,
    }

    return dates_delta_cal_dict


def gen_cal_get_offsite_dog_dict():
    # get info on dogs that have offsite circumstances
    host_or_foster_dogs = DogProfile.objects.filter(
        appt_only=False,
        offsite=True,
        shelterluv_status="Available for Adoption").order_by('name')
    
    offsite_dogs = DogProfile.objects.filter(
        offsite=True, 
        shelterluv_status="Available for Adoption").order_by('name')

    offsite_dog_dict = {
        'host_or_foster_dogs': host_or_foster_dogs,
        'offsite_dogs': offsite_dogs
    }

    return offsite_dog_dict


def gen_cal_get_popular_dogs():
    # filter to all dogs with high interest (10+ adopters)
    all_dogs = get_all_available_dogs()
    popular_dogs = [dog.name for dog in all_dogs if calc_popularity(dog)]
    return popular_dogs
    

def gen_cal_get_short_notice_dict(date):
    # get all short notice objects for context
    sn_add = ShortNotice.objects.filter(date=date, sn_status="1")
    sn_cancel = ShortNotice.objects.filter(date=date, sn_status="2")
    sn_move = ShortNotice.objects.filter(date=date, sn_status="3")
    sn_show = True if len(ShortNotice.objects.filter(date=date)) > 0 else False

    short_notice_dict = {
        'sn_add': sn_add,
        'sn_cancel': sn_cancel,
        'sn_move': sn_move,
        'sn_show': sn_show,
    }

    return short_notice_dict


def gen_cal_get_timeslots_dict(date, load, user, user_groups):
    # call for timeslot filter and set some scheduling parameters
    all_appointments = Appointment.objects.filter(
        appt_type__in=["1", "2", "3"], 
        available=False,
        date=date, 
    )
    application_ids = [[appt.adopter.application_id, appt.adopter.full_name()] 
        for appt in all_appointments]
    is_staff = 'greeter' in user_groups or 'admin' in user_groups
    timeslots_query = [slot for slot in Timeslot.objects.filter(date=date)]
    
    empty_day_db = True if timeslots_query == [] else False

    if is_staff:
        timeslots = filter_timeslots_admin(timeslots_query, date, load)
    else:
        timeslots = filter_timeslots_adopter(
            timeslots_query, date, user.adopter)

    empty_day = True if timeslots == {} else False

    context = {
        'application_ids': application_ids,
        'empty_day': empty_day,
        'empty_day_db': empty_day_db,
        'schedulable': ["1", "2", "3"],
        'timeslots': timeslots,
    }

    return context


def get_empty_days():
    # see what days are missing appointments in upcoming 14 days
    global today
    empty_dates = []

    for d in [today + datetime.timedelta(days=x) for x in range(14)]:
        appts_for_date = list(Appointment.objects.filter(date=d))

        #discard if it's a weekend
        if len(appts_for_date) <= 10 and d.weekday() < 5:
            empty_dates += [[d, date_str(d)]]   

    return empty_dates


def get_no_outcome_appts():
    # see appointments in past 7 days without outcome entered
    global today
    no_outcome_appts = []

    for d in [today - datetime.timedelta(days=x) for x in range(7, 0, -1)]:
        check_for_appts = list(Appointment.objects.filter(
            appt_type__lte=3, 
            available=False,
            date=d, 
            outcome=1, 
        ))

        for appt in check_for_appts:
            no_outcome_appts += [appt]

    return no_outcome_appts

