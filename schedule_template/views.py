from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from .models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate
import datetime
from django.contrib.auth.models import Group, User
from dashboard.decorators import *

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def weekly(request):
    dows = Daily_Schedule.objects

    context = {
        'dows': dows,
    }

    return render(request, "schedule_template/weekly_schedule.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def daily(request, dow_id):
    daily_sched = get_object_or_404(Daily_Schedule, pk=dow_id)
    daily_sched_timeslots = [time for time in daily_sched.timeslots.all()]
    daily_sched_appts = {}

    for time in daily_sched_timeslots:
        daily_sched_appts[time] = [appt for appt in time.appointments.all()]

    context = {
        'daily_sched': daily_sched,
        'timeslots': daily_sched_timeslots,
        'appointments': daily_sched_appts,
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
        hour = int(data['hour'])
        minute = int(data['minute'])
        daypart = data['daypart']

        if daypart == "1" and hour < 12:
            hour += 12

        new_ts = TimeslotTemplate.objects.create(day_of_week = dow.day_of_week, time = datetime.time(hour, minute))
        dow.timeslots.add(TimeslotTemplate.objects.latest('id'))

        return redirect('daily', dow_id)
    else:
        form = NewTimeslotModelForm(request.POST or None, initial={'daypart': "1"})

    context = {
        'form': form,
        'dow': dow,
    }

    return render(request, "schedule_template/timeslot_form.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_appointment(request, dow_id, timeslot_id):
    dow = Daily_Schedule.objects.get(pk=dow_id)
    timeslot = TimeslotTemplate.objects.get(pk=timeslot_id)
    form = GenericAppointmentModelFormPrefilled(request.POST or None, initial={'day_of_week': dow.day_of_week, 'time': timeslot.time})
    if form.is_valid():
        form.save()
        timeslot.appointments.add(AppointmentTemplate.objects.latest('id'))
        return redirect('daily', dow_id)
    else:
        form = GenericAppointmentModelFormPrefilled(initial={'day_of_week': dow.day_of_week, 'time': timeslot.time})

    context = {
        'form': form,
        'dow': dow,
        'timeslot': timeslot,
    }

    return render(request, "schedule_template/render_form.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_appointment(request, dow_id, appt_id):
    appt = AppointmentTemplate.objects.get(pk=appt_id)
    form = GenericAppointmentModelFormPrefilled(request.POST or None, instance=appt)
    if form.is_valid():
        form.save()
        return redirect('daily', dow_id)
    else:
        form = GenericAppointmentModelFormPrefilled(request.POST or None, instance=appt)

    context = {
        'form': form,
    }

    return render(request, "schedule_template/render_form.html", context)
