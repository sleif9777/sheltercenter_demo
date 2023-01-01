import datetime

from django.contrib.auth.models import Group, User
from django.shortcuts import render, get_object_or_404, redirect

from .forms import *
from .models import AppointmentTemplate, Daily_Schedule, TimeslotTemplate
from dashboard.decorators import *

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def weekly(request):
    dows = Daily_Schedule.objects
    context = {
        'dows': dows,
        'page_title': "Weekly Template",
    }

    return render(request, "schedule_template/weekly_schedule.html", context)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def daily(request, dow_id):
    daily_sched = get_object_or_404(Daily_Schedule, pk=dow_id)
    all_timeslots = daily_sched.timeslots.all()
    daily_sched_timeslots = [time for time in all_timeslots]
    daily_sched_appts = {}

    for time in daily_sched_timeslots:
        all_appts = time.appointments.all()
        daily_sched_appts[time] = [appt for appt in all_appts]

    context = {
        'appointments': daily_sched_appts,
        'daily_sched': daily_sched,
        'page_title': "Edit {0} Template".format(daily_sched.dow_string()),
        'timeslots': daily_sched_timeslots,
    }

    return render(request, "schedule_template/daily_schedule.html", context)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def delete_timeslot(request, dow_id, timeslot_id):
    deleted_timeslot = get_object_or_404(TimeslotTemplate, pk=timeslot_id)
    deleted_timeslot.delete()

    return redirect('daily', dow_id)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def delete_appointment(request, dow_id, appt_id):
    deleted_appt = get_object_or_404(AppointmentTemplate, pk=appt_id)
    deleted_appt.delete()

    return redirect('daily', dow_id)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_timeslot(request, dow_id):
    dow = Daily_Schedule.objects.get(pk=dow_id)
    form = NewTimeslotModelForm(request.POST or None, initial={'daypart': "1"})

    if form.is_valid():
        data = form.cleaned_data
        daypart = data['daypart']
        hour = int(data['hour'])
        minute = int(data['minute'])
        is_pm = daypart == "1"

        if is_pm and hour < 12:
            hour += 12

        TimeslotTemplate.objects.create(
            day_of_week=dow.day_of_week,
            time=datetime.time(hour, minute))
        dow.timeslots.add(TimeslotTemplate.objects.latest('id'))

        return redirect('daily', dow_id)
    else:
        form = NewTimeslotModelForm(request.POST or None, initial={'daypart': "1"})

    context = {
        'dow': dow,
        'form': form,
        'form_instructions': "Add a timeslot.",
        'page_header': "Add Timeslot",
        'page_title': "Add Timeslot",
    }

    return render(request, "appt_calendar/render_form.html", context)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_appointment(request, dow_id, timeslot_id):
    dow = Daily_Schedule.objects.get(pk=dow_id)
    timeslot = TimeslotTemplate.objects.get(pk=timeslot_id)

    form = GenericAppointmentModelFormPrefilled(
        request.POST or None, 
        initial={
            'day_of_week': dow.day_of_week, 
            'time': timeslot.time
        }
    )
    
    if form.is_valid():
        form.save()
        timeslot.appointments.add(AppointmentTemplate.objects.latest('id'))
        return redirect('daily', dow_id)
    else:
        form = GenericAppointmentModelFormPrefilled(
            initial={
                'day_of_week': dow.day_of_week, 
                'time': timeslot.time
            }
        )

    context = {
        'dow': dow,
        'form': form,
        'form_instructions': "Add an appointment to the timeslot.",
        'page_header': "Add Appointment",
        'page_title': "Add Appointment",
        'timeslot': timeslot,
    }

    return render(request, "appt_calendar/render_form.html", context)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_appointment(request, dow_id, appt_id):
    appt = AppointmentTemplate.objects.get(pk=appt_id)
    form = GenericAppointmentModelFormPrefilled(
        request.POST or None, instance=appt)
    
    if form.is_valid():
        form.save()
        return redirect('daily', dow_id)
    else:
        form = GenericAppointmentModelFormPrefilled(
            request.POST or None, instance=appt)

    context = {
        'form': form,
        'form_instructions': "Fill in the details below.",
        'page_header': "Edit Appointment",
        'page_title': "Edit Appointment",
    }

    return render(request, "appt_calendar/render_form.html", context)
