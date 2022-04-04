from django.shortcuts import render, get_object_or_404, redirect
import datetime, time
from schedule_template.models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate, SystemSettings
from .models import Timeslot, Appointment
from adopter.models import Adopter
from .forms import *
from emails.email_template import *
from email_mgr.email_sender import *
from .date_time_strings import *
from .appointment_manager import *
from dashboard.views import generate_calendar as gc

#
# # Create your views here.
#

system_settings = SystemSettings.objects.get(pk=1)

def calendar_home(request):
    today = datetime.date.today()
    return redirect('calendar', "admin")

def calendar(request, role):
    today = datetime.date.today()
    return redirect('calendar_date', role, today.year, today.month, today.day)

def copy_temp_to_cal(request, date_year, date_month, date_day, role):
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

    for adopter in all_adopters.iterator():
        if adopter.alert_date == date:
            dates_are_open(adopter, date)

    return redirect('calendar_date', role, date.year, date.month, date.day)

def set_alert_date(request, role, adopter_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    adopter = Adopter.objects.get(pk=adopter_id)

    adopter.alert_date = date
    adopter.save()

    alert_date_set(adopter, date)

    return redirect('adopter_calendar_date', role, adopter_id, date.year, date.month, date.day)

def greeter_reschedule(request, role, adopter_id, appt_id, date_year, date_month, date_day, source):
    old_appt = Appointment.objects.get(pk=appt_id)
    old_appt.outcome = "1"
    old_appt.save()

    adopter = Adopter.objects.get(pk=adopter_id)
    full_name = adopter.adopter_full_name()

    context = {
        "full_name": full_name,
        "adopter": adopter,
        "appt": old_appt,
        "source": source,
    }

    calendar = gc(role, 'reschedule', None, date_year, date_month, date_day)

    context.update(calendar)

    return render(request, "appt_calendar/calendar_greeter_reschedule.html/", context)
#
def adopter_calendar_date(request, role, adopter_id, date_year, date_month, date_day):
    adopter = Adopter.objects.get(pk=adopter_id)

    try:
        current_appt = Appointment.objects.filter(adopter_choice=adopter).latest('id') #.exclude(date__lt = today)
        current_appt_str = current_appt.date_and_time_string()
    except:
        current_appt = None
        current_appt_str = None

    context = {
        'adopter': adopter,
        'current_appt': current_appt,
        'current_appt_str': current_appt_str
    }

    calendar = gc(role, 'full', adopter_id, date_year, date_month, date_day)

    context.update(calendar)

    return render(request, 'appt_calendar/calendar_test_harness.html', context)

def book_appointment(request, role, adopter_id, appt_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    adopter = Adopter.objects.get(pk=adopter_id)

    if appt.available == False and appt.adopter_choice != adopter:

        context = {
            'adopter': adopter,
            'role': role,
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

            return redirect('adopter_calendar_date', role, adopter_id, date.year, date.month, date.day)
        else:

            form = BookAppointmentForm(request.POST or None, instance=appt, initial={'adopter_choice': adopter})

        context = {
            'form': form,
            'adopter': adopter,
        }

        return render(request, "appt_calendar/bookappt.html", context)

def jump_to_date_greeter(request, role, adopter_id, appt_id):
    form = JumpToDateForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data
        date = data['date']

        return redirect('greeter_reschedule', role, adopter_id, appt_id, date.year, date.month, date.day)
    else:
        form = JumpToDateForm(request.POST or None, initial={'date': datetime.date.today()})

    context = {
        'form': form,
        'role': role,
    }

    return render(request, "appt_calendar/jump_to_date.html", context)

def jump_to_date_admin(request, role):
    form = JumpToDateForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data
        date = data['date']

        return redirect('calendar_date', role, date.year, date.month, date.day)
    else:
        form = JumpToDateForm(request.POST or None, initial={'date': datetime.date.today()})

    context = {
        'form': form,
        'role': role,
    }

    return render(request, "appt_calendar/jump_to_date.html", context)

def jump_to_date_adopter(request, role, adopter_id):
    form = JumpToDateForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data
        date = data['date']

        return redirect('adopter_calendar_date', role, adopter_id, date.year, date.month, date.day)
    else:
        form = JumpToDateForm(request.POST or None, initial={'date': datetime.date.today()})

    context = {
        'form': form,
        'role': role,
        'adopter': Adopter.objects.get(pk=adopter_id),
    }

    return render(request, "appt_calendar/jump_to_date.html", context)

def calendar_date(request, role, date_year, date_month, date_day):
    context = gc(role, 'full', None, date_year, date_month, date_day)

    return render(request, "appt_calendar/calendar_test_harness.html", context)

def paperwork_calendar(request, role, date_year, date_month, date_day, appt_id, hw_status):
    appt = Appointment.objects.get(pk=appt_id)

    if hw_status == 'positive':
        fta_or_adoption = "FTA"
    else:
        fta_or_adoption = "Adoption"

    calendar = gc(role, 'full', None, date_year, date_month, date_day)

    context = {
        "appt": appt,
        "hw_status": hw_status,
        "fta_or_adoption": fta_or_adoption,
    }

    context.update(calendar)

    return render(request, "appt_calendar/paperwork_calendar.html/", context)

def calendar_print(request, role, date_year, date_month, date_day):
    context = gc(role, 'full', None, date_year, date_month, date_day)

    return render(request, "appt_calendar/calendar_print.html/", context)

def daily_report_all_appts(request, role, date_year, date_month, date_day):
    context = gc(role, 'full', None, date_year, date_month, date_day)

    return render(request, "appt_calendar/daily_report_all_appts.html/", context)

def daily_reports_home(request, role):
    date = datetime.date.today()

    context = {
        "date": date,
        "role": role,
    }

    return render(request, "appt_calendar/daily_report_home.html/", context)

def chosen_board(request, role):
    all_dows = Daily_Schedule.objects
    today = datetime.date.today()
    appointments = Appointment.objects
    appt_list = []

    for appt in appointments.iterator():
        appt_list += [appt]

    context = {
        "all_dows": all_dows,
        "role": role,
        "today": today,
        "appointments": appt_list,
    }

    return render(request, "appt_calendar/chosen_board.html/", context)

def daily_report_adopted_chosen_fta(request, role, date_year, date_month, date_day):
    context = gc(role, 'full', None, date_year, date_month, date_day)

    return render(request, "appt_calendar/daily_report_adopted_chosen_fta.html/", context)

def send_followup(request, role, appt_id, date_year, date_month, date_day, host):
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

    return redirect('calendar_date', role, date.year, date.month, date.day)

def send_followup_w_host(request, role, appt_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)

    appt.outcome = "5"
    appt.comm_followup = True
    appt.save()

    adopter = appt.adopter_choice

    follow_up_w_host(adopter)

    adopter.has_current_appt = False
    adopter.visits_to_date += 1
    adopter.save()

    return redirect('calendar_date', role, date.year, date.month, date.day)

def delete_timeslot(request, role, date_year, date_month, date_day, timeslot_id):
    date = datetime.date(date_year, date_month, date_day)
    deleted_timeslot = get_object_or_404(Timeslot, pk=timeslot_id)
    deleted_timeslot.delete()

    return redirect('calendar_date', role, date.year, date.month, date.day)

def add_appointment(request, role, date_year, date_month, date_day, timeslot_id):
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

        return redirect('calendar_date', role, date.year, date.month, date.day)
    else:
        form = AppointmentModelFormPrefilled(initial={'date': date, 'time': timeslot.time})

    context = {
        'form': form,
        'date': date,
        'timeslot': timeslot,
        'title': "Add Appointment",
        'role': role,
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

def add_paperwork_appointment(request, role, date_year, date_month, date_day, timeslot_id, originalappt_id):
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

        return redirect('chosen_board', role)
    else:
        form = AppointmentModelFormPrefilled(initial={'date': date, 'time': timeslot.time, 'appt_type': paperwork_appt_type, 'adopter_choice': original_appt.adopter_choice, 'available': False, 'published': False, 'dog': original_appt.dog})

    context = {
        'form': form,
        'date': date,
        'timeslot': timeslot,
        'title': "Add Paperwork Appointment",
        'role': role,
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

def edit_appointment(request, role, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)

    if role == 'adopter':
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
                confirm_etemp(appt.adopter_choice, appt)
                # confirm(appt.time, appt.date, appt.adopter_choice, appt)

                if appt.date == datetime.date.today():
                    notify_adoptions_add(appt.adopter_choice, appt)

            delist_appt(appt)

        if role == 'adopter':
            return redirect('adopter_calendar_date', role, appt.adopter_choice.id, date.year, date.month, date.day)
        else:
            return redirect('calendar_date', role, date.year, date.month, date.day)
    else:
        if role == 'adopter':
            form = BookAppointmentForm(request.POST or None, instance=appt)
        else:
            form = AppointmentModelFormPrefilled(request.POST or None, instance=appt)

    context = {
        'form': form,
        'title': "Edit Appointment",
        'role': role,
        'adopter': appt.adopter_choice,
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

def enter_decision(request, role, appt_id, date_year, date_month, date_day):
    appt = Appointment.objects.get(pk=appt_id)
    form = ApptOutcomeForm(request.POST or None, instance=appt)
    today = datetime.date.today()

    if form.is_valid():
        form.save()

        appt.adopter_choice.has_current_appt = False
        appt.adopter_choice.save()

        adopter = appt.adopter_choice

        if appt.outcome == "5":
            adopter.visits_to_date += 1
            follow_up(adopter)
        elif appt.outcome in ["2", "3", "4"]:
            adopter.visits_to_date = 0

            if appt.outcome == "3":
                chosen(adopter, appt)

        adopter.save()

        if role == "admin":
            return redirect('calendar_date', role, today.year, today.month, today.day)
        elif role == "greeter":
            return redirect('calendar', role)

    else:
        form = ApptOutcomeForm(request.POST or None, instance=appt)

    context = {
        'form': form,
        'role': role,
    }

    return render(request, "appt_calendar/enter_decision_form.html", context)

def remove_adopter(request, role, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    adopter = appt.adopter_choice

    cancel(adopter, appt)

    adopter.has_current_appt = False
    adopter.save()

    reset_appt(appt)

    return redirect('calendar_date', role, date.year, date.month, date.day)

def validate_adopter_action(request, role, action, adopter_id, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    adopter = Adopter.objects.get(pk=adopter_id)

    context = {
        'adopter': adopter,
        'date': date,
        'appt': appt,
        'action': action
    }

    return render(request, "appt_calendar/adopter_validate_action.html", context)

def adopter_self_cancel(request, role, adopter_id, date_year, date_month, date_day, appt_id):
    complete = False

    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    adopter = appt.adopter_choice

    cancel(adopter, appt)

    adopter.has_current_appt = False
    adopter.save()

    reset_appt(appt)

    if appt.date == datetime.date.today():
        notify_adoptions_cancel(appt, adopter)

    appt_str = appt.date_and_time_string()

    context = {
        'adopter': adopter,
        'appt_str': appt_str,
    }

    return render(request, "appt_calendar/adopter_self_cancel.html", context)

def adopter_reschedule(request, role, adopter_id, appt_id, date_year, date_month, date_day, source):
    adopter = Adopter.objects.get(pk=adopter_id)
    date = datetime.date(date_year, date_month, date_day)
    appt_set = Appointment.objects.filter(adopter_choice=adopter.id).exclude(date__lt = datetime.date.today())

    current_appt_set = Appointment.objects.filter(adopter_choice=adopter.id).exclude(date__lt = datetime.date.today())

    current_appt = None

    for a in current_appt_set.iterator():
        current_appt = a

    new_appt = Appointment.objects.get(pk=appt_id)

    if new_appt.available == False and new_appt.adopter_choice != adopter:
        context = {
            'adopter': adopter,
            'role': role,
            'appt': Appointment.objects.get(pk=appt_id),
            'date': date,
        }

        return render(request, "appt_calendar/appt_not_available.html", context)
    else:
        new_appt.internal_notes = current_appt.internal_notes
        new_appt.adopter_notes = current_appt.adopter_notes
        new_appt.bringing_dog = current_appt.bringing_dog
        new_appt.has_cat = current_appt.has_cat
        new_appt.mobility = current_appt.mobility

        if role == "adopter" or (role == "admin" and source == "calendar"):
            reset_appt(current_appt)
            current_appt.save()

        new_appt.adopter_choice = adopter
        adopter.has_current_appt = True
        adopter.save()

        new_appt.save()

        if role == "adopter":
            delist_appt(new_appt)

            reschedule(adopter, new_appt)

            if current_appt.date == datetime.date.today():
                notify_adoptions_reschedule_cancel(adopter, current_appt, new_appt)
            elif new_appt.date == datetime.date.today():
                notify_adoptions_reschedule_add(adopter, current_appt, new_appt)

            return redirect("adopter_calendar_date", role, adopter_id, date_year, date_month, date_day)
        else:
            today = datetime.date.today()

            if role == "greeter" or (role == 'admin' and source == "followup"):
                current_appt.outcome = "5"
                current_appt.save()
                adopter.visits_to_date += 1
                adopter.save()
                greeter_reschedule_email(adopter, new_appt)
            elif role == "admin":

                if current_appt.date == datetime.date.today():
                    notify_adoptions_reschedule_cancel(adopter, current_appt, new_appt)
                elif new_appt.date == datetime.date.today():
                    notify_adoptions_reschedule_add(adopter, current_appt, new_appt)

                reschedule(adopter, new_appt)

            delist_appt(new_appt)
            return redirect("calendar_date", role, today.year, today.month, today.day)

def delete_appointment(request, role, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    deleted_appt = get_object_or_404(Appointment, pk=appt_id)
    deleted_appt.delete()

    return redirect('calendar_date', role, date.year, date.month, date.day)

def add_timeslot(request, role, date_year, date_month, date_day):
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

        return redirect('calendar_date', role, date.year, date.month, date.day)
    else:
        form = NewTimeslotModelForm(request.POST or None, initial={'daypart': "1"})

    context = {
        'form': form,
        'date': date,
        'role': role,
    }

    return render(request, "appt_calendar/new_timeslot_form.html", context)
