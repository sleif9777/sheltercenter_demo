<<<<<<< HEAD
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
from adopter.models import Adopter
from appt_calendar.appointment_manager import *
from appt_calendar.date_time_strings import *
from appt_calendar.forms import *
from appt_calendar.models import *
from email_mgr.email_sender import *
from schedule_template.models import AppointmentTemplate, Daily_Schedule, TimeslotTemplate, SystemSettings
from wishlist.models import Dog
from wishlist.views import get_and_update_dogs

system_settings = SystemSettings.objects.get(pk=1)

# Create your views here.

def register(request):

    form = CreateAdminForm()

    if request.method == "POST":
        form = CreateAdminForm(request.POST)

        if form.is_valid():
            form.save()

    context = {
        'form': form,
    }

    return render(request, 'dashboard/register.html', context)


@unauthenticated_user
def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            user_groups = set(group.name for group in user.groups.iterator())

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
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            user_groups = set(group.name for group in user.groups.iterator())

            if user_groups != {'adopter'}:
                login(request, user)
                return redirect('calendar')
            else:
                return redirect('login')

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

    logout(request)

    return redirect('login')


def gc_get_user_info(user):
    user_groups = set(group.name for group in user.groups.all().iterator())

    try:
        current_appt = Appointment.objects.filter(adopter=user.adopter).latest('id')
        current_appt_str = current_appt.date_and_time_string()
    except:
        current_appt = None
        current_appt_str = None   

    return user_groups, current_appt, current_appt_str


def gc_set_dates(date):
    #create a formatted string and weekday string
    date_pretty = date_str(date)
    weekday = weekday_str(date)

    #set today, previous, and next, calculate delta
    today = datetime.date.today()
    next_day = date + datetime.timedelta(days=1)
    previous_day = date - datetime.timedelta(days=1)
    delta = (date - datetime.date.today()).days    

    return date_pretty, weekday, today, next_day, previous_day, delta


def gc_get_empty_dates(today):
    empty_dates = []

    #check for empty dates in next 14 days
    for d in [today + datetime.timedelta(days=x) for x in range(14)]:
        check_for_appts = list(Appointment.objects.filter(date = d))

        #moot if it's a weekend
        if len(check_for_appts) <= 10 and d.weekday() < 5:
            empty_dates += [[d, date_str(d)]]

    return empty_dates


def gc_get_no_decision_appts(today):
    no_outcome_appts = []
    
    #check for any appointments in past 7 days without outcomes
    for d in [today - datetime.timedelta(days=x) for x in range(7, 0, -1)]:
        check_for_appts = list(Appointment.objects.filter(date = d, appt_type__lte=3, outcome=1, available=False))

        for appt in check_for_appts:
            no_outcome_appts += [appt]

    return no_outcome_appts


def gc_get_announcements(date):
    #retrieve the daily announcement if one exists
    try:
        daily_announcement = DailyAnnouncement.objects.get(date = date)
    except:
        daily_announcement = None

    #retrieve the internal announcement if one exists
    try:
        internal_announcement = InternalAnnouncement.objects.get(date = date)
    except:
        internal_announcement = None

    #retrieve the overarching announcement if one exists
    try:
        calendar_announcement = CalendarAnnouncement.objects.get(pk=1)
    except:
        calendar_announcement = None

    #retrieve the list of offsite dogs
    offsite_dogs = Dog.objects.filter(offsite=True, shelterluv_status="Available for Adoption").order_by('name')

    return daily_announcement, internal_announcement, calendar_announcement, offsite_dogs


def gc_is_empty(timeslots):
    #check if date is empty after filtering
    if timeslots == {}:
        empty_day = True
    else:
        empty_day = False

    return empty_day


def gc_filter_appts_internal(load, date, timeslots_query):
    timeslots = {}
    
    #load all appointments
    if load == 'full':
        for time in timeslots_query:
            timeslots[time] = list(time.appointments.filter(date = date, time = time.time))

    #load only available schedulable appointments
    elif load == 'reschedule':
        for time in timeslots_query:
            timeslots[time] = list(time.appointments.filter(date = date, time = time.time, appt_type__in = ["1", "2", "3"]))
            timeslots[time] = [appt for appt in timeslots[time] if appt.adopter is None]

            #delete unnecessary timeslots
            if timeslots[time] == []:
                timeslots.pop(time)

    empty_day = gc_is_empty(timeslots)

    return timeslots, empty_day


def gc_filter_appts_adopter(current_appt, date, timeslots_query):
    timeslots = {}

    for time in timeslots_query:
        #calculate the timeslots datetime, the current time, and the cutoff period (2 hours later)
        dt_time = datetime.datetime(time.date.year, time.date.month, time.date.day, time.time.hour, time.time.minute)
        now = datetime.datetime.now()
        cutoff = now + datetime.timedelta(hours=2)

        #if past or less than two hours from now, show no appts
        if cutoff >= dt_time:
            timeslots[time] = []

        #else show appointments
        else:
            timeslots[time] = list(time.appointments.filter(date = date, time = time.time, appt_type__in = ["1", "2", "3"]))

            # if the adopter's appointment is in timeslot, only show that
            if current_appt is not None and current_appt in timeslots[time]:
                timeslots[time] = [current_appt]
            # else show all open appts in schedulable
            else:
                timeslots[time] = [appt for appt in timeslots[time] if appt.adopter is None]

        #delete unnecessary timeslots
        if timeslots[time] == []:
            timeslots.pop(time)

    empty_day = gc_is_empty(timeslots)

    return timeslots, empty_day
    

def gc_get_short_notice(date):
    sn_add = ShortNotice.objects.filter(date = date, sn_status = "1")
    sn_cancel = ShortNotice.objects.filter(date = date, sn_status = "2")
    sn_move = ShortNotice.objects.filter(date = date, sn_status = "3")

    if len(ShortNotice.objects.filter(date=date)) > 0:
        sn_show = True
    else:
        sn_show = False

    return sn_add, sn_cancel, sn_move, sn_show


def generate_calendar(user, load, adopter_id, date_year, date_month, date_day):
    #get user groups and current appt if applicable
    user_groups, current_appt, current_appt_str = gc_get_user_info(user)

    #set the date from the integers, get date-related info
    date = datetime.date(date_year, date_month, date_day)
    date_pretty, weekday, today, next_day, previous_day, delta = gc_set_dates(date)

    #set message viewing defaults
    empty_dates = gc_get_empty_dates(today)
    no_outcome_appts = gc_get_no_decision_appts(today)

    #get announcements
    daily_announcement, internal_announcement, calendar_announcement, offsite_dogs = gc_get_announcements(date)

    #adopters should not see if more than two weeks into future
    if delta <= 13:
        visible = True
    else:
        visible = False

    #create a list of timeslots
    timeslots_query = [timeslot for timeslot in Timeslot.objects.filter(date = date)]

    #adopters should only see open appointments or their own
    #for the timeslot they currently are in, they should only see their own appointment
    if 'adopter' in user_groups:
        timeslots, empty_day = gc_filter_appts_adopter(current_appt, date, timeslots_query)
    #admins and greeters should see all appointments
    else:
        timeslots, empty_day = gc_filter_appts_internal(load, date, timeslots_query)

    #get short notices
    sn_add, sn_cancel, sn_move, sn_show = gc_get_short_notice(date)

    context = {
        "date": date,
        "date_pretty": date_pretty,
        "weekday": weekday,
        "today": today,
        "next_day": next_day,
        "previous_day": previous_day,
        "delta": delta,
        "empty_dates": empty_dates,
        "no_outcome_appts": no_outcome_appts,
        'daily_announcement': daily_announcement,
        'calendar_announcement': calendar_announcement,
        'internal_announcement': internal_announcement,
        'offsite_dogs': offsite_dogs,
        "visible": visible,
        "timeslots": timeslots,
        "empty_day": empty_day,
        'sn_add': sn_add,
        'sn_cancel': sn_cancel,
        'sn_move': sn_move,
        'sn_show': sn_show,
        "schedulable": ["1", "2", "3"],
        'page_title': "Calendar",
    }

    return context


def test_harness(request):
    context = generate_calendar('admin', 'full', None, 2022, 4, 4)
    return render(request, 'appt_calendar/calendar_test_harness.html', context)


@authenticated_user
@allowed_users(allowed_roles={'superuser'})
def images(request):
    return render(request, 'dashboard/images.html')


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_signature(request):
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
    return render(request, "dashboard/fake500.html")


def error_500(request):
    headers = {
        'X-Api-Key': os.environ.get('SHELTERLUV_API_KEY'),
    }

    #get a random dog request
    request_address = 'https://www.shelterluv.com/api/v1/animals?status_type=publishable'
    dogs_request = requests.get(request_address, headers=headers).json()
    display_dog = random.choice(list(dogs_request['animals']))

    #get dog attributes
    dog_img = display_dog['CoverPhoto']
    dog_name = display_dog['Name']
    dog_sex = display_dog['Sex']
    dog_breed = display_dog['Breed']

    try:
        dog_weight = "{0} lbs., ".format(display_dog['CurrentWeightPounds'])
    except:
        return ""

    age_months = int(display_dog['Age'])
    dog_age = "Age {0}Y {1}M".format(age_months // 12, age_months % 12)

    context = {
        'dog_img': dog_img,
        'dog_name': dog_name,
        'dog_sex': dog_sex,
        'dog_breed': dog_breed,
        'dog_weight': dog_weight,
        'dog_age': dog_age,
    }

    return render(request, 'dashboard/500.html', context)
>>>>>>> css_refactor
