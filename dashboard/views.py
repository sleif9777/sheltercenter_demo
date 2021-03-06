from django.shortcuts import render, redirect
import datetime, time
from schedule_template.models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate, SystemSettings
from appt_calendar.models import *
from adopter.models import Adopter
from appt_calendar.forms import *
from email_mgr.email_sender import *
from appt_calendar.date_time_strings import *
from appt_calendar.appointment_manager import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .decorators import *
from .models import *
from .forms import *

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

def generate_calendar(user, load, adopter_id, date_year, date_month, date_day):
    user_groups = set(group.name for group in user.groups.all().iterator())

    try:
        current_appt = Appointment.objects.filter(adopter=user.adopter).latest('id')
        current_appt_str = current_appt.date_and_time_string()
    except:
        current_appt = None
        current_appt_str = None

    #set the date from the integers, create a formatted string
    date = datetime.date(date_year, date_month, date_day)
    date_pretty = date_str(date)

    #set today, previous, and next, calculate delta
    today = datetime.date.today()
    next_day = date + datetime.timedelta(days=1)
    previous_day = date - datetime.timedelta(days=1)
    delta_from_today = (date - datetime.date.today()).days

    #set message viewing defaults
    empty_dates = []
    no_outcome_appts = []
    upload_current = True

    #if role is admin and calendar is empty, set weekday string for button text
    weekday = weekday_str(date)

    #if admin, generate the following info for messages
    if 'admin' in user_groups:

        #check for empty dates in next 14 days
        for d in [today + datetime.timedelta(days=x) for x in range(14)]:
            check_for_appts = list(Appointment.objects.filter(date = d))

            #moot if it's a weekend
            if len(check_for_appts) <= 10 and d.weekday() < 5:
                empty_dates += [[d, date_str(d)]]

        #check when adopters were last uploaded
        print("Today", today)
        print("Range", [today - datetime.timedelta(days=x) for x in range(2)])
        print("Datapoint", system_settings.last_adopter_upload)
        print("Bool", system_settings.last_adopter_upload not in [today - datetime.timedelta(days=x) for x in range(2)])
        if system_settings.last_adopter_upload not in [today - datetime.timedelta(days=x) for x in range(2)]:
            upload_current = False

        #check for any appointments in past 7 days without outcomes
        for d in [today - datetime.timedelta(days=x) for x in range(7, 0, -1)]:
            check_for_appts = list(Appointment.objects.filter(date = d, appt_type__lte=3, outcome=1, available=False))

            for appt in check_for_appts:
                no_outcome_appts += [appt]

    #retrieve the daily announcement if one exists
    try:
        daily_announcement = DailyAnnouncement.objects.get(date = date)
    except:
        daily_announcement = None

    #retrieve the daily announcement if one exists
    try:
        internal_announcement = InternalAnnouncement.objects.get(date = date)
    except:
        internal_announcement = None

    #retrieve the daily announcement if one exists
    try:
        calendar_announcement = CalendarAnnouncement.objects.get(pk=1)
        print(calendar_announcement.text)
    except:
        calendar_announcement = None

    #adopters should not see if more than two weeks into future
    if delta_from_today <= 13:
        visible_to_adopters = True
    else:
        visible_to_adopters = False

    #create a list of timeslots
    timeslots_query = [timeslot for timeslot in Timeslot.objects.filter(date = date)]
    timeslots = {}

    #admins and greeters should see all appointments
    if 'greeter' in user_groups or 'admin' in user_groups:
        if load == 'full':
            for time in timeslots_query:
                timeslots[time] = list(time.appointments.filter(date = date, time = time.time))
        elif load == 'reschedule':
            for time in timeslots_query:
                timeslots[time] = list(time.appointments.filter(date = date, time = time.time, appt_type__in = ["1", "2", "3"]))
                timeslots[time] = [appt for appt in timeslots[time] if appt.adopter is None]

                #delete unnecessary timeslots
                if timeslots[time] == []:
                    timeslots.pop(time)

    #adopters should only see open appointments or their own
    #for the timeslot they currently are in, they should only see their own appointment
    elif 'adopter' in user_groups:
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
                # else show all open appts in scheduleable
                else:
                    timeslots[time] = [appt for appt in timeslots[time] if appt.adopter is None]

            #delete unnecessary timeslots
            if timeslots[time] == []:
                timeslots.pop(time)

    if timeslots == {}:
        empty_day = True
    else:
        empty_day = False

    sn_add = ShortNotice.objects.filter(date = date, sn_status = "1")
    print('sn_add', sn_add)
    sn_cancel = ShortNotice.objects.filter(date = date, sn_status = "2")
    print('sn_add', sn_add)
    sn_move = ShortNotice.objects.filter(date = date, sn_status = "3")
    print('sn_add', sn_add)

    if len(ShortNotice.objects.filter(date=date)) > 0:
        sn_show = True
    else:
        sn_show = False

    print(ShortNotice.objects.filter(date=date))
    print('sn_show', sn_show)

    context = {
        "date": date,
        "date_pretty": date_pretty,
        "next_day": next_day,
        "previous_day": previous_day,
        "weekday": weekday,
        "timeslots": timeslots,
        "empty_day": empty_day,
        "empty_dates": empty_dates,
        "upload_current": upload_current,
        "schedulable": ["1", "2", "3"],
        "visible": visible_to_adopters,
        "delta": delta_from_today,
        "today": today,
        "no_outcome_appts": no_outcome_appts,
        'page_title': "Calendar",
        'daily_announcement': daily_announcement,
        'calendar_announcement': calendar_announcement,
        'internal_announcement': internal_announcement,
        'sn_add': sn_add,
        'sn_cancel': sn_cancel,
        'sn_move': sn_move,
        'sn_show': sn_show,
    }

    print(context)

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

def edit_help(request):

    return render(request, "email_mgr/edit_help.html", context)

def help(request):

    return render(request, "email_mgr/help.html", context)
