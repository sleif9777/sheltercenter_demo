from django.shortcuts import render, get_object_or_404, redirect
import datetime, time
from schedule_template.models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate, SystemSettings
from .models import Timeslot, Appointment
from adopter.models import Adopter
from .forms import *
from email_mgr.email_sender import *
from .date_time_strings import *
from .appointment_manager import *
from dashboard.views import generate_calendar as gc
from django.contrib.auth.models import Group, User
from dashboard.decorators import *

system_settings = SystemSettings.objects.get(pk=1)

def get_groups(user_obj):
    try:
        user_groups = set(group.name for group in user_obj.groups.all().iterator())
    except:
        user_groups = set()

    return user_groups

def calendar(request):
    today = datetime.date.today()
    return redirect('calendar_date', today.year, today.month, today.day)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def copy_temp_to_cal(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    daily_sched_temp = get_object_or_404(Daily_Schedule, day_of_week=date.weekday())
    all_adopters = Adopter.objects

    for timeslot in daily_sched_temp.timeslots.iterator():
        new_timeslot_for_cal = Timeslot(date = date, time = timeslot.time)
        new_timeslot_for_cal.save()
        get_appts = timeslot.appointments.all()
        for appt in get_appts:
            new_appt_for_cal = Appointment(date = date, time = timeslot.time, appt_type = appt.appt_type)
            new_appt_for_cal.save()
            new_timeslot_for_cal.appointments.add(Appointment.objects.latest('id'))

    adopters_to_alert = [adopter for adopter in Adopter.objects.filter(alert_date = date)]

    for adopter in adopters_to_alert:
        dates_are_open(adopter, date)

    return redirect('calendar_date', date.year, date.month, date.day)

def set_alert_date(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    adopter = request.user.adopter

    adopter.alert_date = date
    adopter.save()

    alert_date_set(adopter, date)

    return redirect('calendar_date', date.year, date.month, date.day)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def greeter_reschedule(request, adopter_id, appt_id, date_year, date_month, date_day, source):
    try:
        old_appt = Appointment.objects.get(pk=appt_id)
        old_appt.outcome = "1"
        old_appt.save()
    except:
        old_appt = Appointment.objects.create()

    adopter = Adopter.objects.get(pk=adopter_id)
    full_name = adopter.adopter_full_name()

    if 'source' == 'edit':
        action = "Scheduling"
    else:
        action = 'Rescheduling'

    context = {
        "full_name": full_name,
        "adopter": adopter,
        "appt": old_appt,
        "source": source,
        "action": action,
    }

    calendar = gc(request.user, 'reschedule', None, date_year, date_month, date_day)

    context.update(calendar)

    return render(request, "appt_calendar/calendar_greeter_reschedule.html/", context)

def book_appointment(request, appt_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    adopter = request.user.adopter

    if appt.available == False and appt.adopter_choice != adopter:

        context = {
            'adopter': adopter,
        }

        return render(request, "appt_calendar/appt_not_available.html", context)

    else:
        form = BookAppointmentForm(request.POST or None, instance=appt)

        if form.is_valid():
            form.save()

            adopter.has_current_appt = True
            adopter.save()

            appt.adopter_choice = adopter
            delist_appt(appt)

            confirm_etemp(adopter, appt)

            if appt.date == datetime.date.today():
                notify_adoptions_add(adopter, appt)

            return redirect('calendar')
        else:

            form = BookAppointmentForm(request.POST or None, instance=appt, initial={'adopter_choice': adopter})

        context = {
            'form': form,
            'adopter': adopter,
        }

        return render(request, "appt_calendar/bookappt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def jump_to_date_greeter(request, adopter_id, appt_id):
    form = JumpToDateForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data
        date = data['date']

        return redirect('greeter_reschedule', adopter_id, appt_id, date.year, date.month, date.day)
    else:
        form = JumpToDateForm(request.POST or None, initial={'date': datetime.date.today()})

    context = {
        'form': form,
    }

    return render(request, "appt_calendar/jump_to_date.html", context)

def jump_to_date(request):
    form = JumpToDateForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data
        date = data['date']

        return redirect('calendar_date', date.year, date.month, date.day)
    else:
        form = JumpToDateForm(request.POST or None, initial={'date': datetime.date.today()})

    context = {
        'form': form,
    }

    return render(request, "appt_calendar/jump_to_date.html", context)

def calendar_date(request, date_year, date_month, date_day):
    try:
        user_groups = set(group.name for group in request.user.groups.all().iterator())
    except:
        user_groups = set()

    context = gc(request.user, 'full', None, date_year, date_month, date_day)
    #
    # context['role'] = 'admin'
    #
    # if 'superuser' in user_groups or 'admin' in user_groups:
    #     context['role'] = 'admin'
    # elif 'greeter' in user_groups:
    #     context['role'] = 'greeter'
    if 'adopter' in user_groups:
        # context['role'] = 'adopter'
        try:
            current_appt = Appointment.objects.filter(adopter_choice=request.user.adopter).latest('id') #.exclude(date__lt = today)
            current_appt_str = current_appt.date_and_time_string()
        except:
            current_appt = None
            current_appt_str = None

        adopter_context = {
            'current_appt': current_appt,
            'current_appt_str': current_appt_str
        }

        context.update(adopter_context)

    return render(request, "appt_calendar/calendar_test_harness.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def paperwork_calendar(request, date_year, date_month, date_day, appt_id, hw_status):
    appt = Appointment.objects.get(pk=appt_id)

    if hw_status == 'positive':
        fta_or_adoption = "FTA"
    else:
        fta_or_adoption = "Adoption"

    calendar = gc(request.user, 'full', None, date_year, date_month, date_day)

    context = {
        "appt": appt,
        "hw_status": hw_status,
        "fta_or_adoption": fta_or_adoption,
    }

    context.update(calendar)

    return render(request, "appt_calendar/paperwork_calendar.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def calendar_print(request, date_year, date_month, date_day):
    context = gc('admin', 'full', None, date_year, date_month, date_day)

    return render(request, "appt_calendar/calendar_print.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def daily_report_all_appts(request, date_year, date_month, date_day):
    context = gc('admin', 'full', None, date_year, date_month, date_day)

    return render(request, "appt_calendar/daily_report_all_appts.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def daily_reports_home(request):
    date = datetime.date.today()

    context = {
        "date": date,
    }

    return render(request, "appt_calendar/daily_report_home.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def chosen_board(request):
    today = datetime.date.today()
    appointments = [appt for appt in Appointment.objects.filter(outcome__in = ["3", "6", "7"], paperwork_complete=False)]

    context = {
        "today": today,
        "appointments": appointments,
    }

    return render(request, "appt_calendar/chosen_board.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def remove_from_chosen_board(request, appt_id):
    appt = Appointment.objects.get(pk=appt_id)

    appt.dog = ""
    appt.outcome = "5"
    appt.save()

    return redirect('chosen_board')

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def mark_complete_on_chosen_board(request, appt_id):
    appt = Appointment.objects.get(pk=appt_id)

    appt.paperwork_complete = True
    appt.save()

    return redirect('chosen_board')

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def daily_report_adopted_chosen_fta(request, date_year, date_month, date_day):
    context = gc('admin', 'full', None, date_year, date_month, date_day)

    return render(request, "appt_calendar/daily_report_adopted_chosen_fta.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def send_followup(request, appt_id, date_year, date_month, date_day, host):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)

    appt.outcome = "5"
    appt.comm_followup = True
    appt.save()

    adopter = appt.adopter_choice

    if host == 0:
        follow_up(adopter)
    else:
        follow_up_w_host(adopter)

    adopter.has_current_appt = False
    adopter.visits_to_date += 1
    adopter.save()

    return redirect('calendar_date', date.year, date.month, date.day)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def delete_timeslot(request, date_year, date_month, date_day, timeslot_id):
    date = datetime.date(date_year, date_month, date_day)
    deleted_timeslot = get_object_or_404(Timeslot, pk=timeslot_id)
    deleted_timeslot.delete()

    return redirect('calendar_date', date.year, date.month, date.day)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_appointment(request, date_year, date_month, date_day, timeslot_id):
    date = datetime.date(date_year, date_month, date_day)
    timeslot = Timeslot.objects.get(pk=timeslot_id)
    form = AppointmentModelFormPrefilled(request.POST or None, initial = {'date': date, 'time': timeslot.time})
    if form.is_valid():
        form.save()
        appt = Appointment.objects.latest('id')
        timeslot.appointments.add(appt)

        if int(appt.appt_type) > 3:
            delist_appt(appt)

        if appt.adopter_choice != None:

            adopter = appt.adopter_choice
            adopter.has_current_appt = True
            adopter.save()

            delist_appt(appt)

            confirm_etemp(adopter, appt)

            if appt.date == datetime.date.today():
                notify_adoptions_add(adopter, appt)

        return redirect('calendar_date', date.year, date.month, date.day)
    else:
        form = AppointmentModelFormPrefilled(initial={'date': date, 'time': timeslot.time})

    context = {
        'form': form,
        'date': date,
        'timeslot': timeslot,
        'title': "Add Appointment",
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_paperwork_appointment(request, date_year, date_month, date_day, timeslot_id, originalappt_id):
    date = datetime.date(date_year, date_month, date_day)
    timeslot = Timeslot.objects.get(pk=timeslot_id)
    original_appt = Appointment.objects.get(pk=originalappt_id)

    if original_appt.heartworm == True:
        paperwork_appt_type = "6"
    else:
        paperwork_appt_type = "5"

    form = AppointmentModelFormPrefilled(request.POST or None, initial = {'date': date, 'time': timeslot.time, 'appt_type': paperwork_appt_type, 'adopter_choice': original_appt.adopter_choice, 'available': False, 'published': False, 'dog': original_appt.dog})

    if form.is_valid():
        form.save()
        appt = Appointment.objects.latest('id')
        timeslot.appointments.add(appt)

        original_appt.outcome = "7"
        original_appt.save()

        if appt.adopter_choice != None:

            adopter = appt.adopter_choice
            adopter.has_current_appt = False
            adopter.save()

            delist_appt(appt)

            adoption_paperwork(adopter, appt, original_appt.heartworm)

        return redirect('chosen_board')
    else:
        form = AppointmentModelFormPrefilled(initial={'date': date, 'time': timeslot.time, 'appt_type': paperwork_appt_type, 'adopter_choice': original_appt.adopter_choice, 'available': False, 'published': False, 'dog': original_appt.dog})

    context = {
        'form': form,
        'date': date,
        'timeslot': timeslot,
        'title': "Add Paperwork Appointment",
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_appointment(request, date_year, date_month, date_day, appt_id):
    try:
        user_groups = set(group.name for group in request.user.groups.all().iterator())
    except:
        user_groups = set()

    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    original_adopter = appt.adopter_choice

    if user_groups == {'adopter'}:
        form = BookAppointmentForm(request.POST or None, instance=appt)
    else:
        form = AppointmentModelFormPrefilled(request.POST or None, instance=appt)

    if appt.adopter_choice != None:
        current_email = appt.adopter_choice.adopter_email
    else:
        current_email = None

    if form.is_valid():
        form.save()

        try:
            post_save_email = appt.adopter_choice.adopter_email
        except:
            post_save_email = None
        if appt.adopter_choice != None:
            if appt.appt_type in ["1", "2", "3"]:

                if original_adopter != appt.adopter_choice:
                    confirm_etemp(appt.adopter_choice, appt)

                    if original_adopter != None:
                        cancel(original_adopter, appt)

                if appt.date == datetime.date.today():
                    notify_adoptions_add(appt.adopter_choice, appt)

                appt.adopter_choice.has_current_appt = True
                appt.adopter_choice.save()

            delist_appt(appt)

        return redirect('calendar_date', date.year, date.month, date.day)
    else:
        if user_groups == {'adopter'}:
            form = BookAppointmentForm(request.POST or None, instance=appt)
        else:
            form = AppointmentModelFormPrefilled(request.POST or None, instance=appt)

    context = {
        'form': form,
        'title': "Edit Appointment",
        'adopter': appt.adopter_choice,
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def enter_decision(request, appt_id, date_year, date_month, date_day):
    appt = Appointment.objects.get(pk=appt_id)
    form = ApptOutcomeForm(request.POST or None, instance=appt)
    today = datetime.date.today()

    if form.is_valid():
        form.save()

        adopter = appt.adopter_choice

        adopter.has_current_appt = False

        if appt.outcome == "5":
            adopter.visits_to_date += 1
            follow_up(adopter)
        elif appt.outcome in ["2", "3", "4"]:
            adopter.visits_to_date = 0

            if appt.outcome == "3":
                chosen(adopter, appt)

        adopter.save()

        return redirect('calendar')

    else:
        form = ApptOutcomeForm(request.POST or None, instance=appt)

    context = {
        'form': form,
    }

    return render(request, "appt_calendar/enter_decision_form.html", context)

def remove_adopter(request, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    adopter = appt.adopter_choice

    cancel(adopter, appt)

    adopter.has_current_appt = False
    adopter.save()

    reset_appt(appt)

    if get_groups(request.user) == {'adopter'}:
        if appt.date == datetime.date.today():
            notify_adoptions_cancel(appt, adopter)

        appt_str = appt.date_and_time_string()

        context = {
            'adopter': adopter,
            'appt_str': appt_str,
        }

        return render(request, "appt_calendar/adopter_self_cancel.html", context)

    else:
        return redirect('calendar_date', date.year, date.month, date.day)

def adopter_reschedule(request, adopter_id, appt_id, date_year, date_month, date_day, source):
    adopter = Adopter.objects.get(pk=adopter_id)
    date = datetime.date(date_year, date_month, date_day)
    appt_set = Appointment.objects.filter(adopter_choice=adopter.id).exclude(date__lt = datetime.date.today())
    user_groups = get_groups(request.user)

    try:
        current_appt = [appt for appt in Appointment.objects.filter(adopter_choice=adopter.id).exclude(date__lt = datetime.date.today())][0]
    except:
        pass

    new_appt = Appointment.objects.get(pk=appt_id)

    if new_appt.available == False and new_appt.adopter_choice != adopter:
        context = {
            'adopter': adopter,
            'appt': Appointment.objects.get(pk=appt_id),
            'date': date,
        }

        return render(request, "appt_calendar/appt_not_available.html", context)
    else:
        try:
            new_appt.internal_notes = current_appt.internal_notes
            new_appt.adopter_notes = current_appt.adopter_notes
            new_appt.bringing_dog = current_appt.bringing_dog
            new_appt.has_cat = current_appt.has_cat
            new_appt.mobility = current_appt.mobility
        except:
            pass

        if user_groups == {"adopter"} or ("admin" in user_groups and source == "calendar"):
            reset_appt(current_appt)
            current_appt.save()

        new_appt.adopter_choice = adopter
        adopter.has_current_appt = True

        adopter.save()
        new_appt.save()

        if user_groups == {"adopter"}:
            delist_appt(new_appt)

            reschedule(adopter, new_appt)

            if current_appt.date == datetime.date.today():
                notify_adoptions_reschedule_cancel(adopter, current_appt, new_appt)
            elif new_appt.date == datetime.date.today():
                notify_adoptions_reschedule_add(adopter, current_appt, new_appt)

            return redirect("calendar_date", date_year, date_month, date_day)
        else:
            today = datetime.date.today()

            if ('greeter' in user_groups and 'admin' not in user_groups) or ('admin' in user_groups and source == "followup"):
                try:
                    current_appt.outcome = "5"
                    current_appt.save()
                    adopter.visits_to_date += 1
                    adopter.save()
                    greeter_reschedule_email(adopter, new_appt)
                except:
                    pass
            elif 'admin' in user_groups:

                try:
                    if current_appt.date == datetime.date.today():
                        notify_adoptions_reschedule_cancel(adopter, current_appt, new_appt)
                except:
                    if new_appt.date == datetime.date.today():
                        notify_adoptions_reschedule_add(adopter, current_appt, new_appt)

                adopter.has_current_appt = True
                adopter.save()

                delist_appt(new_appt)

                if source == "edit":
                    confirm_etemp(adopter, new_appt)
                    return redirect('edit_adopter', adopter.id)
                else:
                    reschedule(adopter, new_appt)
                    return redirect("calendar_date", today.year, today.month, today.day)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def delete_appointment(request, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    deleted_appt = get_object_or_404(Appointment, pk=appt_id)
    deleted_appt.delete()

    return redirect('calendar_date', date.year, date.month, date.day)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_timeslot(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)

    form = NewTimeslotModelForm(request.POST or None, initial={"daypart": "1"})

    if form.is_valid():
        data = form.cleaned_data
        hour = int(data['hour'])
        minute = int(data['minute'])
        daypart = data['daypart']

        if daypart == "1" and hour < 12:
            hour += 12

        new_ts = Timeslot.objects.create(date = date, time = datetime.time(hour, minute))

        return redirect('calendar_date', date.year, date.month, date.day)
    else:
        form = NewTimeslotModelForm(request.POST or None, initial={'daypart': "1"})

    context = {
        'form': form,
        'date': date,
    }

    return render(request, "appt_calendar/new_timeslot_form.html", context)
