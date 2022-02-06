from django.shortcuts import render, get_object_or_404, redirect
from .forms import GenericTimeslotModelFormPrefilled, GenericAppointmentModelFormPrefilled, NewTimeslotModelForm
from .models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate
import datetime

def weekly(request):
    dows = Daily_Schedule.objects
    today = datetime.date.today()

    context = {
        'dows': dows,
        'today': today,
        'role': 'admin',
    }

    return render(request, "schedule_template/weekly_schedule.html", context)

def daily(request, dow_id):
    daily_sched = get_object_or_404(Daily_Schedule, pk=dow_id)
    daily_sched_timeslots = daily_sched.timeslots.all()
    daily_sched_appts = {}
    all_dows = Daily_Schedule.objects
    today = datetime.date.today()

    for time in daily_sched_timeslots.iterator():
        get_appts = time.appointments.all()
        appts_for_time = []
        for appointment in get_appts:
            appts_for_time += [appointment]
        daily_sched_appts[time] = appts_for_time
        #print(daily_sched_appts)

    context = {
        'daily_sched': daily_sched,
        'timeslots': daily_sched_timeslots,
        'appointments': daily_sched_appts,
        'all_dows': all_dows,
        'today': today,
        'role': 'admin',
    }

    return render(request, "schedule_template/daily_schedule.html", context)

def delete_timeslot(request, dow_id, timeslot_id):
    deleted_timeslot = get_object_or_404(TimeslotTemplate, pk=timeslot_id)
    deleted_timeslot.delete()

    return redirect('daily', dow_id)

def delete_appointment(request, dow_id, appt_id):
    deleted_appt = get_object_or_404(AppointmentTemplate, pk=appt_id)
    deleted_appt.delete()

    return redirect('daily', dow_id)

def add_timeslot(request, dow_id):
    dow = Daily_Schedule.objects.get(pk=dow_id)

    form = NewTimeslotModelForm(request.POST or None, initial={'daypart': "1"})

    if form.is_valid():
        data = form.cleaned_data
        hour = int(data['hour'])
        minute = int(data['minute'])
        daypart = data['daypart']

        if daypart == "1":
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

def add_appointment(request, dow_id, timeslot_id):
#    dow_id -= 2
    dow = Daily_Schedule.objects.get(pk=dow_id)
    timeslot = TimeslotTemplate.objects.get(pk=timeslot_id)
    #form = GenericTimeslotModelForm(request.POST or None, initial={"day_of_week": dow.day_of_week})
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

def edit_appointment(request, dow_id, appt_id):
#    dow_id -= 2
    appt = AppointmentTemplate.objects.get(pk=appt_id)
    #form = GenericTimeslotModelForm(request.POST or None, initial={"day_of_week": dow.day_of_week})
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

# def detail(request, blog_id):
#     detailblog = get_object_or_404(Blog, pk=blog_id)
#     return render(request, 'blog/detail.html', {'blog': detailblog})

# Create your views here.
