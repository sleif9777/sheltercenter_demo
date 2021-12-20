from django.shortcuts import render, get_object_or_404, redirect
import datetime
from schedule_template.models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate
from .models import Timeslot, Appointment
from adopter.models import Adopter
from .forms import *
from emails.email_template import *
#
# # Create your views here.
#
# def calendar_home(request):
#     today = datetime.date.today()
#     return redirect('calendar_date', today.year, today.month, today.day, "adopter")

def calendar(request, role):
    today = datetime.date.today()

    return redirect('calendar_date', role, today.year, today.month, today.day)
#
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

def greeter_reschedule(request, role, adopter_id, appt_id, date_year, date_month, date_day):
    all_dows = Daily_Schedule.objects
    date = datetime.date(date_year, date_month, date_day)
    date_pretty = date.strftime("%A, %B %#d, %Y")
    next_day = date + datetime.timedelta(days=1)
    previous_day = date - datetime.timedelta(days=1)
    today = datetime.date.today()
    weekday = date.strftime("%A")
    timeslots_query = Timeslot.objects.filter(date = date)
    timeslots = {}
    open_timeslots = []
    delta_from_today = (date - datetime.date.today()).days
    old_appt = Appointment.objects.get(pk=appt_id)

    old_appt.outcome = "1"
    old_appt.save()

    adopter = Adopter.objects.get(pk=adopter_id)
    full_name = adopter.adopter_full_name()

    print(adopter)

    if delta_from_today <= 13:
        visible_to_adopters = True
    else:
        visible_to_adopters = False

    for time in timeslots_query.iterator():
        get_appts = time.appointments.filter(date = date, time = time.time)
        appts_for_time = []
        add_to_open_timeslots = False
        for appointment in get_appts:
            appts_for_time += [appointment]
            if appointment.available == True:
                add_to_open_timeslots = True
        timeslots[time] = appts_for_time
        if add_to_open_timeslots == True:
            open_timeslots += [time]

    if timeslots == {}:
        empty_day = True
    else:
        empty_day = False

    context = {
        "date": date,
        "date_pretty": date_pretty,
        "next_day": next_day,
        "previous_day": previous_day,
        "weekday": weekday,
        "timeslots": timeslots,
        "empty_day": empty_day,
        "schedulable": ["1", "2", "3"],
        "all_dows": all_dows,
        "visible": visible_to_adopters,
        "delta": delta_from_today,
        "role": role,
        "open_timeslots": open_timeslots,
        "full_name": full_name,
        "today": today,
        "adopter": adopter,
        "appt": old_appt,
    }

    return render(request, "appt_calendar/calendar_greeter_reschedule.html/", context)
#
def adopter_calendar_date(request, role, adopter_id, date_year, date_month, date_day):
    adopter = Adopter.objects.get(pk=adopter_id)
    all_dows = Daily_Schedule.objects
    date = datetime.date(date_year, date_month, date_day)
    date_pretty = date.strftime("%A, %B %#d, %Y")
    today = datetime.date.today()
    next_day = date + datetime.timedelta(days=1)
    previous_day = date - datetime.timedelta(days=1)
    weekday = date.strftime("%A")
    timeslots_query = Timeslot.objects.filter(date = date)
    timeslots = {}
    open_timeslots = []
    delta_from_today = (date - datetime.date.today()).days

    try:
        current_appt = Appointment.objects.filter(adopter_choice=adopter).latest('id')
        current_appt_str = current_appt.date_and_time_string()
    except:
        current_appt = None
        current_appt_str = None

    has_current_appt = adopter.has_current_appt

    if delta_from_today <= 13:
        visible_to_adopters = True
    else:
        visible_to_adopters = False

    for time in timeslots_query.iterator():
        now = datetime.datetime.now().time()
        if date == today:
            if time.time > now:
                get_appts = time.appointments.filter(date = date, time = time.time)
                appts_for_time = []
                add_to_open_timeslots = False
                for appointment in get_appts:
                    appts_for_time += [appointment]
                    if appointment.available == True:
                        add_to_open_timeslots = True
                timeslots[time] = appts_for_time
                if add_to_open_timeslots == True:
                    open_timeslots += [time]
        else:
            get_appts = time.appointments.filter(date = date, time = time.time)
            appts_for_time = []
            add_to_open_timeslots = False
            for appointment in get_appts:
                appts_for_time += [appointment]
                if appointment.available == True:
                    add_to_open_timeslots = True
            timeslots[time] = appts_for_time
            if add_to_open_timeslots == True:
                open_timeslots += [time]

    if timeslots == {}:
        empty_day = True
    else:
        empty_day = False

    context = {
        "adopter": adopter,
        "current_appt": current_appt,
        "current_appt_str": current_appt_str,
        "has_current_appt": has_current_appt,
        "date": date,
        "date_pretty": date_pretty,
        "next_day": next_day,
        "previous_day": previous_day,
        "weekday": weekday,
        "timeslots": timeslots,
        "empty_day": empty_day,
        "schedulable": ["1", "2", "3"],
        "all_dows": all_dows,
        "visible": visible_to_adopters,
        "delta": delta_from_today,
        "role": role,
        "open_timeslots": open_timeslots,
        "today": today,
    }

    return render(request, "appt_calendar/calendar_adopter.html/", context)

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
        adopter.has_current_appt = True
        adopter.save()

        appt.adopter_choice = adopter
        appt.available = False
        appt.published = False
        appt.save()

        confirm(appt.time, appt.date, appt.adopter_choice, appt)

        form = BookAppointmentForm(request.POST or None, instance=appt)

        if form.is_valid():
            form.save()

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
    all_dows = Daily_Schedule.objects
    date = datetime.date(date_year, date_month, date_day)
    date_pretty = date.strftime("%A, %B %#d, %Y")
    today = datetime.date.today()
    next_day = date + datetime.timedelta(days=1)
    previous_day = date - datetime.timedelta(days=1)
    weekday = date.strftime("%A")
    timeslots_query = Timeslot.objects.filter(date = date)
    timeslots = {}
    open_timeslots = []
    delta_from_today = (date - datetime.date.today()).days

    if delta_from_today <= 13:
        visible_to_adopters = True
    else:
        visible_to_adopters = False

    for time in timeslots_query.iterator():
        get_appts = time.appointments.filter(date = date, time = time.time)
        appts_for_time = []
        add_to_open_timeslots = False
        for appointment in get_appts:
            appts_for_time += [appointment]
            if appointment.available == True:
                add_to_open_timeslots = True
        timeslots[time] = appts_for_time
        if add_to_open_timeslots == True:
            open_timeslots += [time]

    if timeslots == {}:
        empty_day = True
    else:
        empty_day = False

    context = {
        "date": date,
        "date_pretty": date_pretty,
        "next_day": next_day,
        "previous_day": previous_day,
        "weekday": weekday,
        "timeslots": timeslots,
        "empty_day": empty_day,
        "schedulable": ["1", "2", "3"],
        "all_dows": all_dows,
        "visible": visible_to_adopters,
        "delta": delta_from_today,
        "role": role,
        "open_timeslots": open_timeslots,
        "today": today,
    }

    if role == "admin":
        return render(request, "appt_calendar/calendar_admin.html/", context)
    elif role == "greeter":
        return render(request, "appt_calendar/calendar_greeter.html/", context)

def paperwork_calendar(request, role, date_year, date_month, date_day, appt_id, hw_status):
    all_dows = Daily_Schedule.objects
    date = datetime.date(date_year, date_month, date_day)
    date_pretty = date.strftime("%A, %B %#d, %Y")
    today = datetime.date.today()
    next_day = date + datetime.timedelta(days=1)
    previous_day = date - datetime.timedelta(days=1)
    weekday = date.strftime("%A")
    timeslots_query = Timeslot.objects.filter(date = date)
    timeslots = {}
    open_timeslots = []
    delta_from_today = (date - datetime.date.today()).days

    if delta_from_today <= 13:
        visible_to_adopters = True
    else:
        visible_to_adopters = False

    for time in timeslots_query.iterator():
        get_appts = time.appointments.filter(date = date, time = time.time)
        appts_for_time = []
        add_to_open_timeslots = False
        for appointment in get_appts:
            appts_for_time += [appointment]
            if appointment.available == True:
                add_to_open_timeslots = True
        timeslots[time] = appts_for_time
        if add_to_open_timeslots == True:
            open_timeslots += [time]

    if timeslots == {}:
        empty_day = True
    else:
        empty_day = False

    appt = Appointment.objects.get(pk=appt_id)

    if hw_status == 'positive':
        fta_or_adoption = "FTA"
    else:
        fta_or_adoption = "Adoption"

    context = {
        "date": date,
        "date_pretty": date_pretty,
        "next_day": next_day,
        "previous_day": previous_day,
        "weekday": weekday,
        "timeslots": timeslots,
        "empty_day": empty_day,
        "schedulable": ["1", "2", "3"],
        "all_dows": all_dows,
        "visible": visible_to_adopters,
        "delta": delta_from_today,
        "role": role,
        "open_timeslots": open_timeslots,
        "today": today,
        "appt": appt,
        "hw_status": hw_status,
        "fta_or_adoption": fta_or_adoption,
    }

    return render(request, "appt_calendar/paperwork_calendar.html/", context)

def daily_report_all_appts(request, role, date_year, date_month, date_day):
    all_dows = Daily_Schedule.objects
    date = datetime.date(date_year, date_month, date_day)
    date_pretty = date.strftime("%A, %B %#d, %Y")
    today = datetime.date.today()
    next_day = date + datetime.timedelta(days=1)
    previous_day = date - datetime.timedelta(days=1)
    weekday = date.strftime("%A")
    timeslots_query = Timeslot.objects.filter(date = date)
    timeslots = {}
    open_timeslots = []
    delta_from_today = (date - datetime.date.today()).days

    if delta_from_today <= 13:
        visible_to_adopters = True
    else:
        visible_to_adopters = False

    for time in timeslots_query.iterator():
        get_appts = time.appointments.filter(date = date, time = time.time)
        appts_for_time = []
        add_to_open_timeslots = False
        for appointment in get_appts:
            appts_for_time += [appointment]
            if appointment.available == True:
                add_to_open_timeslots = True
        timeslots[time] = appts_for_time
        if add_to_open_timeslots == True:
            open_timeslots += [time]

    if timeslots == {}:
        empty_day = True
    else:
        empty_day = False

    context = {
        "date": date,
        "date_pretty": date_pretty,
        "next_day": next_day,
        "previous_day": previous_day,
        "weekday": weekday,
        "timeslots": timeslots,
        "empty_day": empty_day,
        "schedulable": ["1", "2", "3"],
        "all_dows": all_dows,
        "visible": visible_to_adopters,
        "delta": delta_from_today,
        "role": role,
        "open_timeslots": open_timeslots,
        "today": today,
    }

    return render(request, "appt_calendar/daily_report_all_appts.html/", context)

def daily_reports_home(request, role):
    all_dows = Daily_Schedule.objects
    date = datetime.date.today()
    date_pretty = date.strftime("%A, %B %#d, %Y")
    today = datetime.date.today()
    next_day = date + datetime.timedelta(days=1)
    previous_day = date - datetime.timedelta(days=1)
    weekday = date.strftime("%A")
    timeslots_query = Timeslot.objects.filter(date = date)
    timeslots = {}
    open_timeslots = []
    delta_from_today = (date - datetime.date.today()).days

    if delta_from_today <= 13:
        visible_to_adopters = True
    else:
        visible_to_adopters = False

    for time in timeslots_query.iterator():
        get_appts = time.appointments.filter(date = date, time = time.time)
        appts_for_time = []
        add_to_open_timeslots = False
        for appointment in get_appts:
            appts_for_time += [appointment]
            if appointment.available == True:
                add_to_open_timeslots = True
        timeslots[time] = appts_for_time
        if add_to_open_timeslots == True:
            open_timeslots += [time]

    if timeslots == {}:
        empty_day = True
    else:
        empty_day = False

    context = {
        "date": date,
        "date_pretty": date_pretty,
        "next_day": next_day,
        "previous_day": previous_day,
        "weekday": weekday,
        "timeslots": timeslots,
        "empty_day": empty_day,
        "schedulable": ["1", "2", "3"],
        "all_dows": all_dows,
        "visible": visible_to_adopters,
        "delta": delta_from_today,
        "role": role,
        "open_timeslots": open_timeslots,
        "today": today,
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

def send_ready_to_roll_msg(request, role, appt_id, hw_status):
    appt = Appointment.objects.get(pk=appt_id)

    if hw_status == "positive":
        appt.heartworm = True

    appt.outcome = "6"
    appt.save()

    ready_to_roll(appt, hw_status)

    return redirect('chosen_board', role)

def daily_report_adopted_chosen_fta(request, role, date_year, date_month, date_day):
    all_dows = Daily_Schedule.objects
    date = datetime.date(date_year, date_month, date_day)
    date_pretty = date.strftime("%A, %B %#d, %Y")
    today = datetime.date.today()
    next_day = date + datetime.timedelta(days=1)
    previous_day = date - datetime.timedelta(days=1)
    weekday = date.strftime("%A")
    timeslots_query = Timeslot.objects.filter(date = date)
    timeslots = {}
    open_timeslots = []
    delta_from_today = (date - datetime.date.today()).days

    if delta_from_today <= 13:
        visible_to_adopters = True
    else:
        visible_to_adopters = False

    for time in timeslots_query.iterator():
        get_appts = time.appointments.filter(date = date, time = time.time)
        appts_for_time = []
        add_to_open_timeslots = False
        for appointment in get_appts:
            appts_for_time += [appointment]
            if appointment.available == True:
                add_to_open_timeslots = True
        timeslots[time] = appts_for_time
        if add_to_open_timeslots == True:
            open_timeslots += [time]

    if timeslots == {}:
        empty_day = True
    else:
        empty_day = False

    context = {
        "date": date,
        "date_pretty": date_pretty,
        "next_day": next_day,
        "previous_day": previous_day,
        "weekday": weekday,
        "timeslots": timeslots,
        "empty_day": empty_day,
        "schedulable": ["1", "2", "3"],
        "all_dows": all_dows,
        "visible": visible_to_adopters,
        "delta": delta_from_today,
        "role": role,
        "open_timeslots": open_timeslots,
        "today": today,
    }

    return render(request, "appt_calendar/daily_report_adopted_chosen_fta.html/", context)
#
def send_followup(request, role, appt_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)

    appt.outcome = "5"
    appt.save()

    adopter = appt.adopter_choice

    follow_up(adopter)

    adopter.has_current_appt = False
    adopter.save()

    return redirect('calendar_date', role, date.year, date.month, date.day)

def send_followup_w_host(request, role, appt_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)

    appt.outcome = "5"
    appt.save()

    adopter = appt.adopter_choice

    follow_up_w_host(adopter)

    adopter.has_current_appt = False
    adopter.save()

    return redirect('calendar_date', role, date.year, date.month, date.day)

def delete_timeslot(request, role, date_year, date_month, date_day, timeslot_id):
    date = datetime.date(date_year, date_month, date_day)
    deleted_timeslot = get_object_or_404(Timeslot, pk=timeslot_id)
    deleted_timeslot.delete()

    return redirect('calendar_date', role, date.year, date.month, date.day)
#
def add_appointment(request, role, date_year, date_month, date_day, timeslot_id):
    date = datetime.date(date_year, date_month, date_day)
    timeslot = Timeslot.objects.get(pk=timeslot_id)
    form = AppointmentModelFormPrefilled(request.POST or None, initial = {'date': date, 'time': timeslot.time})
    if form.is_valid():
        form.save()
        appt = Appointment.objects.latest('id')
        timeslot.appointments.add(appt)

        if int(appt.appt_type) > 3:
            appt.available = False
            appt.published = False
            appt.save()

        if appt.adopter_choice != None:

            adopter = appt.adopter_choice
            adopter.has_current_appt = True
            adopter.save()

            appt.available = False
            appt.published = False
            appt.save()

            confirm(appt.time, appt.date, appt.adopter_choice, appt)

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

            appt.available = False
            appt.published = False
            appt.save()

            adoption_paperwork(appt.time, appt.date, appt.adopter_choice, appt, original_appt.heartworm)

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
        if current_email != post_save_email and appt.adopter_choice != None:
            confirm(appt.time, appt.date, appt.adopter_choice, appt)
        if appt.adopter_choice != None or appt.appt_type not in ["1", "2", "3"]:
            appt.available = False
            appt.published = False
            appt.save()


        return redirect('calendar_date', role, date.year, date.month, date.day)
    else:
        form = AppointmentModelFormPrefilled(request.POST or None, instance=appt)

    context = {
        'form': form,
        'title': "Edit Appointment",
        'role': role,
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

def enter_decision(request, role, appt_id, date_year, date_month, date_day):
    appt = Appointment.objects.get(pk=appt_id)
    form = ApptOutcomeForm(request.POST or None, instance=appt)

    if form.is_valid():
        form.save()

        appt.adopter_choice.has_current_appt = False
        appt.adopter_choice.save()

        if role == "admin":
            return redirect('calendar_date', role, date_year, date_month, date_day)
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
    cancel(appt.time, appt.date, appt.adopter_choice)

    adopter = appt.adopter_choice
    adopter.has_current_appt = False
    adopter.save()

    appt.adopter_choice = None
    appt.available = True
    appt.published = True
    appt.outcome = "1"
    appt.internal_notes = ""
    appt.adopter_notes = ""
    appt.bringing_dog = False
    appt.save()

    return redirect('calendar_date', role, date.year, date.month, date.day)

def adopter_self_cancel(request, role, adopter_id, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    cancel(appt.time, appt.date, appt.adopter_choice)

    adopter = appt.adopter_choice
    adopter.has_current_appt = False
    adopter.save()

    appt.adopter_choice = None
    appt.available = True
    appt.published = True
    appt.outcome = "1"
    appt.internal_notes = ""
    appt.adopter_notes = ""
    appt.bringing_dog = False
    appt.save()

    return redirect("adopter_calendar_date", role, adopter_id, date.year, date.month, date.day)

def adopter_reschedule(request, role, adopter_id, appt_id, date_year, date_month, date_day):
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
        print("STOP!" + str(adopter))

        return render(request, "appt_calendar/appt_not_available.html", context)
    else:
        new_appt.internal_notes = current_appt.internal_notes
        new_appt.adopter_notes = current_appt.adopter_notes

        new_appt.bringing_dog = current_appt.bringing_dog

        if role == "adopter" or role == "admin":
            current_appt.adopter_choice = None
            current_appt.available = True
            current_appt.published = True
            current_appt.internal_notes = ""
            current_appt.adopter_notes = ""
            current_appt.bringing_dog = False
            current_appt.save()

        new_appt.adopter_choice = adopter
        new_appt.adopter_choice.has_current_appt = False
        new_appt.available = False
        new_appt.published = False
        new_appt.save()

        if role == "adopter":
            reschedule(new_appt.time, new_appt.date, new_appt.adopter_choice, new_appt)
            return redirect("adopter_calendar_date", role, adopter_id, date_year, date_month, date_day)
        elif role == "greeter":
            today = datetime.date.today()
            greeter_reschedule_email(new_appt.time, new_appt.date, new_appt.adopter_choice, new_appt)
            return redirect("calendar_date", role, today.year, today.month, today.day)
        elif role == "admin":
            today = datetime.date.today()
            reschedule(new_appt.time, new_appt.date, new_appt.adopter_choice, new_appt)
            return redirect("calendar_date", role, today.year, today.month, today.day)

def delete_appointment(request, role, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    deleted_appt = get_object_or_404(Appointment, pk=appt_id)
    deleted_appt.delete()

    return redirect('calendar_date', role, date.year, date.month, date.day)

def add_timeslot(request, role, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    form = TimeslotModelFormPrefilled(request.POST or None, initial={"date": date})
    if form.is_valid():
        form.save()
        return redirect('calendar_date', role, date.year, date.month, date.day)
    else:
        form = TimeslotModelFormPrefilled(request.POST or None, initial={"date": date})

    context = {
        'form': form,
        'date': date,
        'role': role,
    }

    return render(request, "appt_calendar/new_timeslot_form.html", context)
