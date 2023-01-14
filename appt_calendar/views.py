# TO DO:
# Continue refactor
# Add comments to each function
# Group and rename functions

import datetime
import sys
import time

from django.db.models import F
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404, redirect, render

from .appointment_manager import *
from .date_time_strings import *
from .forms import *
from .models import *
from adopter.forms import *
from adopter.models import *
from dashboard.decorators import *
from dashboard.views import generate_calendar as gc
from email_mgr.email_sender import *
from schedule_template.models import *

# GLOBAL VARIABLE
today = datetime.date.today()

# REFACTORED
def get_groups(user_obj):
    try:
        user_groups = set(group.name for group in user_obj.groups.all().iterator())
    except:
        user_groups = set()

    return user_groups


# REFACTORED
@authenticated_user
def calendar(request):
    global today
    return redirect('calendar_date', today.year, today.month, today.day)


# REFACTORED
def alert_adopters_open_date(date):
    adopters_to_alert = [adopter for adopter in Adopter.objects.filter(alert_date=date)]
    for adopter in adopters_to_alert:
        dates_are_open(adopter, date)


# REFACTORED
def create_timeslot_and_appointments_from_template(date):
    daily_sched_temp = get_object_or_404(Daily_Schedule, day_of_week=date.weekday())

    for timeslot in daily_sched_temp.timeslots.iterator():
        new_timeslot_for_cal = Timeslot.objects.create(
            date = date,
            time = timeslot.time
        )
        get_appts = timeslot.appointments.all()

        for appt in get_appts:
            new_appt_for_cal = Appointment.objects.create(
                date = date, 
                time = timeslot.time, 
                appt_type = appt.appt_type
            )
            new_timeslot_for_cal.appointments.add(new_appt_for_cal)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def copy_temp_to_cal(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    create_timeslot_and_appointments_from_template(date)
    alert_adopters_open_date(date)

    return redirect('calendar_date', date.year, date.month, date.day)


# NEEDS REFACTOR (MAYBE COMBINE WITH BELOW FUNCTION)
@authenticated_user
def set_alert_date(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)

    adopter = request.user.adopter
    adopter.alert_date = date
    adopter.save()

    alert_date_set(adopter, date)

    return redirect('edit_adopter', adopter.id)


# NEEDS REFACTOR (MAYBE COMBINE WITH ABOVE FUNCTION)
@authenticated_user
def set_alert_date_greeter(
        request, adopter_id, date_year, date_month, date_day):
    global today
    date = datetime.date(date_year, date_month, date_day)

    adopter = Adopter.objects.get(pk=adopter_id)
    adopter.alert_date = date
    adopter.save()

    alert_date_set(adopter, date)

    return redirect('calendar_date', today.year, today.month, today.day)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def greeter_reschedule(
        request, adopter_id, appt_id, date_year, date_month, date_day, source):
    adopter = Adopter.objects.get(pk=adopter_id)
    full_name = adopter.full_name()
    initial_schedule = source == 'edit' or 'mgmt' in source
    old_appt = Appointment.objects.update_or_create(
        pk=appt_id,
        defaults={"outcome": "1"}
    )[0]

    action = "Schedule" if initial_schedule else "Reschedule"
    action_gerund = "Scheduling" if initial_schedule else "Rescheduling"
    context = {
        "action": action_gerund,
        "adopter": adopter,
        "appt": old_appt,
        "full_name": full_name,
        'page_title': "{0} {1}".format(action, full_name),
        "source": source,
    }

    calendar = gc(request.user, 'reschedule', date_year, date_month, date_day)
    context.update(calendar)
    return render(request, "appt_calendar/calendar_greeter_reschedule.html/", context)


# REFACTORED
def get_default_booking_forms(request, appt, adopter):
    adopter_form = AdopterPreferenceForm(
        request.POST or None,
        instance=adopter
    )
    booking_form = BookAppointmentForm(
        request.POST or None, 
        instance=appt,
        initial={'adopter': adopter}
    )
    return adopter_form, booking_form


def redirect_to_already_booked(request, adopter, appt_id=8296, date=None):
    context = {
        'adopter': adopter,
        'appt': Appointment.objects.get(pk=appt_id),
        'date': date,
        'page_title': "Appointment Not Available",
    }
    return render(request, "appt_calendar/appt_not_available.html", context)


# REFACTORED, BUT NEED TO DELETE DATE VARIABLES
@authenticated_user
def book_appointment(request, appt_id, date_year, date_month, date_day):
    adopter = request.user.adopter
    appt = Appointment.objects.get(pk=appt_id)
    already_booked = appt.adopter is not adopter and not appt.available

    if already_booked:
        redirect_to_already_booked(request, adopter)

        context = {
            'adopter': adopter,
            'page_title': "Appointment Not Available",
        }
        return render(request, "appt_calendar/appt_not_available.html", context)
    else:
        adopter_form, booking_form = get_default_booking_forms(
            request, appt, adopter)

        if booking_form.is_valid() and adopter_form.is_valid():
            if not adopter.has_current_appt:
                save_booking_form(adopter, appt, booking_form, adopter_form)
            
            return redirect('calendar')
        else:
            adopter_form, booking_form = get_default_booking_forms(
                request, appt, adopter)

        context = {
            'adopter': adopter,
            'adopter_form': adopter_form,
            'form': booking_form,
            'page_title': "Book Appointment",
        }
        return render(request, "appt_calendar/bookappt.html", context)


# REFACTORED
def update_or_create_sn_obj(query_appt, query_adopter, current, prev, status):
    sn_obj = ShortNotice.objects.update_or_create(
        date=query_appt.date, adopter=query_adopter,
        defaults={
            'current_appt': current,
            'prev_appt': prev,
            'sn_status': status
        }
    )[0]
    sn_obj.set_backup()


# NEEDS REFACTOR (MAYBE COMBINE WITH BELOW FUNCTION)
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def jump_to_date_greeter(request, adopter_id, appt_id, source):
    form = JumpToDateForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data
        date = data['date']
        return redirect('greeter_reschedule', adopter_id, appt_id, date.year, date.month, date.day, source)
    else:
        form = JumpToDateForm(request.POST or None, initial={'date': datetime.date.today()})

    context = {
        'form': form,
        'form_instructions': "Select a date to jump to on the calendar.",
        'page_header': "Jump To Date",
        'page_title': "Jump To Date",
    }

    return render(request, "appt_calendar/render_form.html", context)


# NEEDS REFACTOR (MAYBE COMBINE WITH ABOVE FUNCTION)
@authenticated_user
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
        'form_instructions': "Select a date to jump to on the calendar.",
        'page_header': "Jump To Date",
        'page_title': "Jump To Date",
    }

    return render(request, "appt_calendar/render_form.html", context)


# REFACTORED
def get_adopter_context(adopter):
    try:
        current_appt = Appointment.objects.filter(
            adopter=adopter).latest('id')
        current_appt_str = current_appt.date_and_time_string()
    except:
        current_appt = None
        current_appt_str = None

    adopter_context = {
        'current_appt': current_appt,
        'current_appt_str': current_appt_str,
        'page_title': "Calendar",
    }
    return adopter_context


# REFACTORED
@authenticated_user
def calendar_date(
    request, date_year, date_month, date_day, appt_id=None, ts_id=None):
    context = gc(request.user, 'full', date_year, date_month, date_day)
    user_groups = get_groups(request.user)

    if appt_id or ts_id:
        if appt_id:
            appt = Appointment.objects.get(pk=appt_id)
            ts_query = Timeslot.objects.get(appointments__id__exact=appt.id)
        else:
            ts_query = Timeslot.objects.get(pk=ts_id)
        redirect_context = {'go_to_div': "ts{0}".format(ts_query.id)}
        context.update(redirect_context)        

    if 'adopter' in user_groups:
        adopter_context = get_adopter_context(request.user.adopter)
        context.update(adopter_context)

    return render(request, "appt_calendar/calendar_test_harness.html", context)


# DEPRECATE?
@authenticated_user
def calendar_date_appt(request, date_year, date_month, date_day, appt_id):
    context = gc(request.user, 'full', date_year, date_month, date_day)
    user_groups = get_groups(request.user)

    try:
        appt = Appointment.objects.get(pk=appt_id)
        ts_query = Timeslot.objects.get(appointments__id__exact=appt.id)
        redirect_context = {'go_to_div': "ts{0}".format(ts_query.id)}
        context.update(redirect_context)
    except:
        pass

    if 'adopter' in user_groups:
        adopter_context = get_adopter_context(request.user.adopter)
        context.update(adopter_context)

    return render(request, "appt_calendar/calendar_test_harness.html", context)


# DEPRECATE?
@authenticated_user
def calendar_date_ts(request, date_year, date_month, date_day, ts_id):
    context = gc(request.user, 'full', date_year, date_month, date_day)
    user_groups = get_groups(request.user)

    try:
        ts_query = Timeslot.objects.get(pk=ts_id)
        redirect_context = {'go_to_div': "ts{0}".format(ts_query.id)}
        context.update(redirect_context)
    except:
        pass

    if 'adopter' in user_groups:
        adopter_context = get_adopter_context(request.user.adopter)
        context.update(adopter_context)

    return render(request, "appt_calendar/calendar_test_harness.html", context)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def paperwork_calendar(
        request, date_year, date_month, date_day, appt_id, hw_status):
    appt = Appointment.objects.get(pk=appt_id)
    fta_or_adoption = "FTA" if hw_status == "positive" else "Adoption"
    calendar = gc(request.user, 'full', date_year, date_month, date_day)
    context = {
        "appt": appt,
        "hw_status": hw_status,
        "fta_or_adoption": fta_or_adoption,
        'page_title': "Calendar",
    }
    context.update(calendar)
    return render(request, "appt_calendar/paperwork_calendar.html/", context)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def calendar_print(request, date_year, date_month, date_day):
    context = gc(request.user, 'full', date_year, date_month, date_day)
    context['page_title'] = "Print Calendar"
    return render(request, "appt_calendar/calendar_print.html/", context)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def report_print(request, date_year, date_month, date_day):
    context = gc(request.user, 'full', date_year, date_month, date_day)
    context['page_title'] = "Daily Report"
    return render(request, "appt_calendar/daily_report_print.html/", context)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def daily_reports_home(request):
    date = today
    return redirect(
        'daily_report_adopted_chosen_fta', date.year, date.month, date.day)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def chosen_board(request):
    global today

    chosen_appointments_query = Appointment.objects.filter(
        outcome__in = ["3", "9", "10"], paperwork_complete=False)
    paper_appointments_query = Appointment.objects.filter(
        outcome__in = ["8"], paperwork_complete=False)
    rtr_appointments_query = Appointment.objects.filter(
        outcome__in = ["7"], paperwork_complete=False)

    chosen_appointments = [appt for appt in chosen_appointments_query.order_by(
        F('outcome').desc(), 'dog')]
    paper_appointments = [appt for appt in paper_appointments_query.order_by('dog')]
    rtr_appointments = [appt for appt in rtr_appointments_query.order_by('dog')]

    context = {
        "chosen_appointments": chosen_appointments,
        'page_title': "Chosen Board",
        "paper_appointments": paper_appointments,
        "rtr_appointments": rtr_appointments,
        "today": today,
    }
    return render(request, "appt_calendar/chosen_board.html/", context)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def revert_to_needs_well_check(request, appt_id):
    appt = Appointment.objects.update_or_create(
        pk=appt_id,
        defaults={
            "outcome": "10"
        }
    )[0]
    date = appt.date
    return redirect('contact_adopter', appt.id, date.year, 
        date.month, date.day, 'no_longer_ready')    


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def remove_from_chosen_board(request, appt_id):
    appt = Appointment.objects.update_or_create(
        pk=appt_id,
        defaults={
            "dog": "",
            "outcome": "5"
        }
    )[0]
    Adopter.objects.update_or_create(
        pk=appt.adopter.id,
        defaults={"waiting_for_chosen": False}
    )
    return redirect('chosen_board')


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def cb_update_status(request, appt_id, outcome):
    Appointment.objects.update_or_create(
        pk=appt_id,
        defaults={"outcome": outcome}
    )
    return redirect('chosen_board')


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def mark_complete_on_chosen_board(request, appt_id):
    appt = Appointment.objects.update_or_create(
        pk=appt_id,
        defaults={"paperwork_complete": True}
    )[0]
    Adopter.objects.update_or_create(
        pk = appt.adopter.id,
        defaults={
            'adoption_complete': True,
            'waiting_for_chosen': False
        }
    )
    return redirect('chosen_board')


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def checked_in_appts(request):
    global today
    context = gc(request.user, 'full', today.year, today.month, today.day)
    return render(request, "appt_calendar/checked_in_appts.html/", context)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def daily_report_adopted_chosen_fta(request, date_year, date_month, date_day):
    context = gc(request.user, 'full', date_year, date_month, date_day)
    return render(request, "appt_calendar/daily_report_adopted_chosen_fta.html/", context)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def send_followup(request, appt_id, date_year, date_month, date_day, host):
    date = datetime.date(date_year, date_month, date_day)
    host = bool(host)
    appt = Appointment.objects.update_or_create(
        pk=appt_id,
        defaults={
            "checked_in": False,
            "checked_out_time": datetime.datetime.now().time(),
            "comm_followup": True,
            "outcome": "5",
        }
    )[0]
    adopter = Adopter.objects.update_or_create(
        pk=appt.adopter.id,
        defaults={
            'has_current_appt': False,
            'visits_to_date': appt.adopter.visits_to_date + 1
        }
    )[0]

    follow_up_w_host(adopter) if host else follow_up(adopter)
    return redirect('calendar_date_appt', date.year, date.month, date.day, appt.id)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def delete_timeslot(request, date_year, date_month, date_day, timeslot_id):
    date = datetime.date(date_year, date_month, date_day)
    deleted_timeslot = get_object_or_404(Timeslot, pk=timeslot_id)
    deleted_timeslot.delete()

    return redirect('calendar_date', date.year, date.month, date.day)


# ANNOUNCEMENTS ALL NEED REFACTORING - TRY TO CONSOLIDATE INTO A SINGLE FUNCTION
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_daily_announcement(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    form = DailyAnnouncementForm(
        request.POST or None, initial = {'date': date})

    if form.is_valid():
        form.save()
        return redirect('calendar_date', date.year, date.month, date.day)
    else:
        form = DailyAnnouncementForm(
            request.POST or None, initial = {'date': date})

    context = {
        'date': date,
        'form': form,
        'title': "Add Calendar Note for {0}".format(date_str(date)),
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_daily_announcement(
    request, announcement_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    announcement = DailyAnnouncement.objects.get(pk=announcement_id)
    form = DailyAnnouncementForm(
        request.POST or None, instance=announcement)

    if form.is_valid():
        form.save()
        return redirect('calendar_date', date.year, date.month, date.day)

    else:
        form = DailyAnnouncementForm(
            request.POST or None, instance=announcement)

    context = {
        'date': date,
        'form': form,
        'title': "Edit Calendar Note for {0}".format(date_str(date)),
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_internal_announcement(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    form = InternalAnnouncementForm(
        request.POST or None, initial = {'date': date})

    if form.is_valid():
        form.save()
        return redirect('calendar_date', date.year, date.month, date.day)

    else:
        form = InternalAnnouncementForm(
            request.POST or None, initial = {'date': date})

    context = {
        'form': form,
        'date': date,
        'title': "Add Calendar Note for {0}".format(date_str(date)),
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_internal_announcement(
    request, announcement_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    announcement = InternalAnnouncement.objects.get(pk = announcement_id)
    form = InternalAnnouncementForm(
        request.POST or None, instance=announcement)

    if form.is_valid():
        form.save()
        return redirect('calendar_date', date.year, date.month, date.day)

    else:
        form = InternalAnnouncementForm(
            request.POST or None, instance=announcement)

    context = {
        'form': form,
        'date': date,
        'title': "Edit Calendar Note for {0}".format(date_str(date)),
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_calendar_announcement(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    announcement = CalendarAnnouncement.objects.latest('id')
    form = CalendarAnnouncementForm(request.POST or None, instance=announcement)

    if form.is_valid():
        form.save()
        return redirect('calendar_date', date.year, date.month, date.day)

    else:
        form = CalendarAnnouncementForm(request.POST or None, instance=announcement)

    context = {
        'form': form,
        'date': date,
        'title': "Add Calendar Note for All Dates",
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_calendar_announcement(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    announcement = CalendarAnnouncement.objects.get(pk = 1)
    form = CalendarAnnouncementForm(request.POST or None, instance=announcement)

    if form.is_valid():
        form.save()
        return redirect('calendar_date', date.year, date.month, date.day)

    else:
        form = CalendarAnnouncementForm(request.POST or None, instance=announcement)

    context = {
        'form': form,
        'date': date,
        'title': "Edit Calendar Note for All Dates",
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)


def handle_add_appointment_form_upon_save(appt, timeslot, date):
    adopter = appt.adopter
    timeslot.appointments.add(appt)

    if not appt.schedulable():
        appt.delist()

    if appt.adopter:
        appt.delist()

        if short_notice(appt):
            appt.mark_short_notice()
            update_or_create_sn_obj(appt, adopter, appt, None, "1")
            notify_adoptions_add(adopter, appt)

        if appt.schedulable():
            return redirect('contact_adopter', appt.id, date.year, date.month, date.day, 'confirm_appt')


# NEEDS REFACTOR
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_appointment(request, date_year, date_month, date_day, timeslot_id):
    date = datetime.date(date_year, date_month, date_day)
    timeslot = Timeslot.objects.get(pk=timeslot_id)
    form = AppointmentModelFormPrefilled(
        request.POST or None, 
        initial={
            'date': date, 
            'time': timeslot.time
        }
    )
    
    if form.is_valid():
        form.save()
        appt = Appointment.objects.latest('id')
        handle_add_appointment_form_upon_save(appt, timeslot, date)
        return redirect('calendar_date_appt', date.year, date.month, date.day, appt.id)
    else:
        form = AppointmentModelFormPrefilled(
            initial={
                'date': date, 
                'time': timeslot.time
            }
        )

    context = {
        'date': date,
        'form': form,
        'timeslot': timeslot,
        'title': "Add Appointment",
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)


# NEEDS REFACTOR
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_followup_appointment(request, adopter_id, date_year, date_month, date_day, timeslot_id):
    date = datetime.date(date_year, date_month, date_day)
    timeslot = Timeslot.objects.get(pk=timeslot_id)
    appt = Appointment.objects.create(date=date, time=timeslot.time)

    timeslot.appointments.add(appt)
    return redirect('adopter_reschedule', adopter_id, appt.id, date_year, date_month, date_day, 'edit')


# REFACTORED
def get_default_paperwork_appt_form(
    request, date, timeslot, original_appt, paperwork_appt_type):
    return AppointmentModelFormPrefilled(
        request.POST or None,
        initial = {
            'adopter': original_appt.adopter,
            'appt_type': paperwork_appt_type,
            'available': False,
            'date': date,
            'dog': original_appt.dog,
            'published': False,
            'time': timeslot.time,
        }
    )


# REFACTORED
def handle_paperwork_appt_form_upon_save(appt, heartworm):
    adopter = appt.adopter
    adopter.has_current_appt = False
    adopter.save()

    appt.delist()

    adoption_paperwork(adopter, appt, heartworm)

    if short_notice(appt):
        appt.mark_short_notice()
        sn_obj = ShortNotice.objects.create(
            current_appt=appt,
            date=appt.date, 
            dog=appt.dog,
            sn_status="1"
        )
        sn_obj.set_backup()
        notify_adoptions_paperwork(appt)


def handle_paperwork_timeslot_in_calendar(appt, timeslot, original_appt):
    timeslot.appointments.add(appt)
    original_appt.outcome = "8"
    original_appt.save()


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_paperwork_appointment(
        request, date_year, date_month, date_day, timeslot_id, originalappt_id):
    date = datetime.date(date_year, date_month, date_day)
    timeslot = Timeslot.objects.get(pk=timeslot_id)
    original_appt = Appointment.objects.get(pk=originalappt_id)
    paperwork_appt_type = "6" if original_appt.heartworm else "5"
    form = get_default_paperwork_appt_form(
        request, date, timeslot, original_appt, paperwork_appt_type)

    if form.is_valid():
        form.save()
        appt = Appointment.objects.latest('id')
        handle_paperwork_timeslot_in_calendar(appt, timeslot, original_appt)

        if appt.adopter:
            handle_paperwork_appt_form_upon_save(appt, original_appt.heartworm)

        return redirect('chosen_board')
    else:
        form = get_default_paperwork_appt_form(
            request, date, timeslot, original_appt, paperwork_appt_type)

    context = {
        'date': date,
        'form': form,
        'timeslot': timeslot,
        'title': "Add Paperwork Appointment",
    }
    return render(request, "appt_calendar/add_edit_appt.html", context)


# REFACTORED
def short_notice(appt):
    global today
    time_now = datetime.datetime.now().time()

    try:
        tomorrow = today + datetime.timedelta(days=1)
        is_today = appt.date == today
        is_tomorrow = appt.date == tomorrow
        booked_after_close = time_now > datetime.time(16,00)

        if is_today or (is_tomorrow and booked_after_close):
            return True
        else:
            return False
    except:
        return False


# REFACTORED
def save_booking_form(adopter, appt, booking_form, adopter_form):
    adopter_form.save()
    booking_form.save()

    adopter.has_current_appt = True
    adopter.save()

    appt.adopter = adopter
    appt.delist()

    confirm_etemp(adopter, appt)

    if short_notice(appt):
        appt.mark_short_notice()
        update_or_create_sn_obj(appt, adopter, appt, None, "1")
        notify_adoptions_add(adopter, appt)


def get_default_edit_appt_forms(request, adopter, appt):
    if only_role(request.user, "adopter"):
        appt_form = EditAppointmentForm(request.POST or None, instance=appt)
        adopter_form = AdopterPreferenceForm(request.POST or None, instance=adopter)
    else:
        if appt.adopter:
            appt_form = AppointmentModelFormPrefilledEdit(request.POST or None, instance=appt)
        else:
            appt_form = AppointmentModelFormPrefilled(request.POST or None, instance=appt)
        adopter_form = None

    return adopter_form, appt_form


def get_current_email(appt):
    if appt.adopter:
        return appt.adopter.primary_email
    else:
        return None


def handle_short_notice_from_edit_appt(appt, adopter):
    appt.mark_short_notice()
    try:
        sn_obj = ShortNotice.objects.get(
            date=appt.date, adopter=adopter, dog=appt.dog)
        sn_current = sn_obj.current_appt
    except:
        sn_current = appt
    update_or_create_sn_obj(appt, adopter, sn_current, None, "1")
    notify_adoptions_add(adopter, appt) 


def handle_appt_delist_from_edit_appt(appt, changed, prev_adopter, date):
    appt.delist()

    if appt.schedulable():
        if changed:
            if prev_adopter:
                cancel(prev_adopter, appt)
        return redirect('contact_adopter', appt.id, date.year, date.month, date.day, 'confirm_appt')
    return


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'adopter'})
def edit_appointment(request, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    current_adopter = appt.adopter
    adopter_form, appt_form = get_default_edit_appt_forms(request, current_adopter, appt)
    current_email = get_current_email(appt)

    if appt_form.is_valid():
        appt_form.save()

        if adopter_form and adopter_form.is_valid():
            adopter_form.save()
        
        post_save_email = get_current_email(appt)
        post_save_adopter = appt.adopter
        email_changed = post_save_email != current_email
        adopter_changed = post_save_adopter != current_adopter

        if email_changed:
            if short_notice(appt):
                handle_short_notice_from_edit_appt(appt, post_save_adopter)

            if appt.adopter:
                handle_appt_delist_from_edit_appt(
                    appt, adopter_changed, current_adopter, date)

        return redirect('calendar_date_appt', date_year, date_month, date_day, appt.id)
    else:
        adopter_form, appt_form = get_default_edit_appt_forms(request, current_adopter, appt)

    context = {
        'adopter': appt.adopter,
        'adopter_form': adopter_form,
        'form': appt_form,
        'title': "Edit Appointment",
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)


def get_default_edit_appt_mgmt_form(request, appt):
    if only_role(request.user, "adopter"):
        form = EditAppointmentForm(request.POST or None, instance=appt)
    else:
        if appt.adopter:
            form = AppointmentModelFormPrefilledEdit(request.POST or None, instance=appt)
        else:
            form = AppointmentModelFormPrefilled(request.POST or None, instance=appt)  

    return form  


def handle_edit_from_mgmt_form_upon_save(form, appt, adopter, date):
    form.save()

    if appt.adopter:
        adopter_changed = adopter not in [None, appt.adopter]
        if adopter_changed:
            cancel(adopter, appt)
            if short_notice(appt):
                appt.mark_short_notice()
                update_or_create_sn_obj(appt, adopter, appt, None, "1")
                notify_adoptions_add(appt.adopter, appt)

        appt.delist()
        return "contact"

    return "edit"


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_appointment_from_mgmt(request, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    current_adopter = appt.adopter
    form = get_default_edit_appt_mgmt_form(request, appt)

    if form.is_valid():
        edit_or_contact = handle_edit_from_mgmt_form_upon_save(
            form, appt, current_adopter, date)

        match edit_or_contact:
            case "contact":
                return redirect('contact_adopter', appt.id, date.year, 
                    date.month, date.day, 'confirm_appt')
            case "edit":
                return redirect('edit_adopter', appt.adopter.id)
    else:
        form = get_default_edit_appt_mgmt_form(request, appt)

    context = {
        'form': form,
        'title': "Edit Appointment",
        'adopter': appt.adopter,
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)


# REFACTORED
def close_out_appointment(appt, adopter):
    # If no decision
    if appt.outcome == "5":
        adopter.visits_to_date += 1
        follow_up(adopter)
    # If decision made
    elif appt.outcome in ["2", "3", "4"]:
        adopter.visits_to_date = 0

    # If decision type falls under chosen umbrella
    if appt.outcome in ["3", "9", "10"]:
        adopter.waiting_for_chosen = True
        chosen(adopter, appt)

    # If dog was taken home (FTA or adoption)
    if appt.outcome in ["2", "4"]:
        adopter.adoption_complete = True

    adopter.has_current_appt = False
    adopter.save()

    appt.checked_in = False
    appt.checked_out_time = datetime.datetime.now().time()
    appt.dog = appt.dog.title()
    appt.last_update_sent = appt.date
    appt.save()


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def enter_decision(request, appt_id, date_year, date_month, date_day):
    appt = Appointment.objects.get(pk=appt_id)
    adopter = appt.adopter
    form = ApptOutcomeForm(request.POST or None, instance=appt)

    if form.is_valid():
        form.save()
        close_out_appointment(appt, adopter)
        return redirect('calendar_date_appt', date_year, date_month, date_day, appt.id)
    else:
        form = ApptOutcomeForm(request.POST or None, instance=appt)

    context = {
        'form': form,
        'form_instructions': "Enter a decision for this appointment.",
        'page_header': "Enter Decision",
        'page_title': "Enter Decision",
    }

    return render(request, "appt_calendar/render_form.html", context)


def only_role(user, group):
    user_groups = get_groups(user)
    return user_groups == {group}


def validate_adopter(appt_adopter, request_adopter):
    return request_adopter == appt_adopter


def remove_adopter_from_appt(appt, adopter):
    if short_notice(appt):
        update_or_create_sn_obj(appt, adopter, None, appt, "2")
        notify_adoptions_cancel(appt, adopter)

    adopter.has_current_appt = False
    adopter.save()
    appt.reset()


def get_user_adopter_or_none(request):
    try:
        return request.user.adopter
    except:
        return None


# REFACTORED
@authenticated_user
def remove_adopter(request, date_year, date_month, date_day, appt_id):
    appt = Appointment.objects.get(pk=appt_id)
    appt_adopter = appt.adopter
    request_adopter = get_user_adopter_or_none(request)
    adopter_only = only_role(request.user, "adopter")

    if adopter_only and not validate_adopter(appt_adopter, request_adopter):
        return redirect('calendar_date_appt', date_year, date_month, date_day, appt.id)
    else:
        if appt.schedulable():
            cancel(appt_adopter, appt)

        remove_adopter_from_appt(appt, appt_adopter)

        if adopter_only:
            appt_str = appt.date_and_time_string()
            context = {
                'adopter': appt_adopter,
                'appt_str': appt_str,
                'page_title': "Appointment Canceled",
            }
            return render(request, "appt_calendar/adopter_self_cancel.html", context)

        return redirect('calendar_date_appt', date_year, date_month, date_day, appt.id)


def determine_short_notice(current, new):
    if short_notice(new):
        new.mark_short_notice()

    return short_notice(current), short_notice(new)


def handle_short_notice_from_reschedule(adopter, current_appt, new_appt):
    current_sn, new_sn = determine_short_notice(current_appt, new_appt)
    
    if current_sn or new_sn:
        if current_sn and new_sn:
            query_appt = new_appt
            current = new_appt
            prev = current_appt
            status = "3"
            notif_type = "time_change"
        elif not current_sn:
            query_appt = new_appt
            current = new_appt
            prev = None
            status = "1"
            notif_type = "add"                    
        elif not new_sn:
            query_appt = current_appt
            current = None
            prev = current_appt
            status = "2"
            notif_type = "cancel"

        update_or_create_sn_obj(query_appt, adopter, current, prev, status)

        match notif_type:
            case "time_change":
                notify_adoptions_time_change(adopter, current_appt, new_appt)
            case "add":
                notify_adoptions_reschedule_add(adopter, current_appt, new_appt)
            case "cancel":
                notify_adoptions_reschedule_cancel(adopter, current_appt, new_appt)


def get_appointments_for_reschedule(adopter, appt_id):
    appt_set = Appointment.objects.filter(
        adopter=adopter.id).exclude(date__lt = datetime.date.today())

    try:
        current_appt = [appt for appt in appt_set][0]
    except:
        current_appt = None

    new_appt = Appointment.objects.get(pk=appt_id)
    return current_appt, new_appt


def copy_appointment_information(current_appt, new_appt, source):
    new_appt.internal_notes = current_appt.internal_notes
    new_appt.adopter_notes = current_appt.adopter_notes
    new_appt.bringing_dog = current_appt.bringing_dog
    new_appt.has_cat = current_appt.has_cat
    new_appt.mobility = current_appt.mobility

    if source == "followup":
        new_appt.appt_type = current_appt.appt_type

    new_appt.save()


def set_up_new_appt(current, new, adopter, source, reset):
    if current:
        copy_appointment_information(current, new, source)

        if reset:
            current.reset()
            current.save()

    new.adopter = adopter
    new.save()
    new.delist()

    adopter.has_current_appt = True
    adopter.save()    


def close_out_current(current_appt, adopter):
    if current_appt:
        current_appt.outcome = "5"
        current_appt.save()
        adopter.visits_to_date += 1
        adopter.save()


# REFACTORED
@authenticated_user
def adopter_reschedule(request, adopter_id, appt_id, date_year, date_month, date_day, source):
    global today
    adopter = Adopter.objects.get(pk=adopter_id)
    date = datetime.date(date_year, date_month, date_day)
    
    current_appt, new_appt = get_appointments_for_reschedule(adopter, appt_id)
    user_groups = get_groups(request.user)
    adopter_only = only_role(request.user, "adopter")
    adopter_validated = validate_adopter(new_appt.adopter, adopter)
    greeter_only = only_role(request.user, "greeter")
    admin_from_calendar = ("admin" in user_groups and source == "calendar")
    admin_from_followup = ("admin" in user_groups and source == "followup")
    reset_current = (adopter_only or admin_from_calendar)

    if not new_appt.available and not adopter_validated:
        redirect_to_already_booked(request, adopter, appt_id, date)
    else:
        set_up_new_appt(current_appt, new_appt, adopter, source, reset_current)

        if greeter_only or admin_from_followup:
            close_out_current(current_appt, adopter)
            greeter_reschedule_email(adopter, new_appt)
            return redirect("calendar_date", today.year, today.month, today.day)
        else:
            handle_short_notice_from_reschedule(adopter, current_appt, new_appt)

            if source == "edit":
                return redirect('edit_cal_appointment_mgmt', new_appt.id, 
                    new_appt.date.year, new_appt.date.month, new_appt.date.day)
            else:
                reschedule(adopter, new_appt)
                return redirect("calendar_date_appt", date_year, date_month, date_day, new_appt.id)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def delete_appointment(request, date_year, date_month, date_day, appt_id):
    deleted_appt = get_object_or_404(Appointment, pk=appt_id)
    adopter = deleted_appt.adopter
    booked = deleted_appt.adopter or deleted_appt.dog
    ts_query = Timeslot.objects.get(appointments__id__exact=deleted_appt.id)

    if booked and deleted_appt.schedulable():
        remove_adopter_from_appt(deleted_appt, adopter)

    deleted_appt.delete()

    return redirect('calendar_date_ts', date_year, date_month, date_day, ts_query.id)


# REFACTORED
def parse_new_timeslot_data(data):
    hour = int(data['hour'])
    minute = int(data['minute'])
    daypart = data['daypart']

    return hour, minute, daypart


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_timeslot(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    form = NewTimeslotModelForm(request.POST or None, initial={"daypart": "1"})

    if form.is_valid():
        data = form.cleaned_data
        hour, minute, daypart = parse_new_timeslot_data(data)

        if daypart == "1" and hour < 12:
            hour += 12

        new_ts = Timeslot.objects.create(
            date = date, time = datetime.time(hour, minute))

        return redirect(
            'calendar_date_ts', date.year, date.month, date.day, new_ts.id)
    else:
        form = NewTimeslotModelForm(
            request.POST or None, initial={'daypart': "1"})

    context = {
        'date': date,
        'form': form,
        'form_instructions': "Select a time to add as a timeslot to the calendar.",
        'page_header': "Add Timeslot",
        'page_title': "Add Timeslot",
    }
    return render(request, "appt_calendar/render_form.html", context)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def toggle_lock(request, appt_id, date_year, date_month, date_day):
    appt = Appointment.objects.get(pk=appt_id)
    appt.locked = not appt.locked
    appt.save()

    return redirect('calendar_date_appt', date_year, date_month, date_day, appt_id)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def check_in_appt(request, appt_id, date_year, date_month, date_day):
    appt = Appointment.objects.update_or_create(
        pk=appt_id,
        defaults={
            "checked_in": True,
            "checked_in_time": datetime.datetime.now().time()
        }
    )[0]
    form = AppointmentCheckInForm(request.POST or None, instance=appt)

    if form.is_valid():
        form.save()
        return redirect(
            'calendar_date_appt', date_year, date_month, date_day, appt_id)
    else:
        form = AppointmentCheckInForm(request.POST or None, instance=appt)

    context = {
        'form': form,
        'form_instructions': "Fill in the information to check in {0}'s appointment.".format(
            appt.adopter.full_name()),
        'page_header': "Check In Appointment",
        'page_title': "Check In Appointment",
    }
    return render(request, "appt_calendar/render_form.html", context)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def toggle_all(request, date_year, date_month, date_day, lock):
    date = datetime.date(date_year, date_month, date_day)
    lock = bool(lock)
    Appointment.objects.filter(
        appt_type__in=["1", "2", "3"],
        date=date, 
    ).update(locked=lock)

    return redirect('calendar_date', date_year, date_month, date_day)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def toggle_time(request, timeslot_id, date_year, date_month, date_day, lock):
    date = datetime.date(date_year, date_month, date_day)
    lock = bool(lock)
    timeslot = Timeslot.objects.get(pk=timeslot_id)
    timeslot.appointments.filter(
        appt_type__in=["1", "2", "3"],
        date=date,
        time=timeslot.time,
    ).update(locked=lock)

    return redirect('calendar_date_ts', date_year, date_month, date_day, timeslot.id)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'adopter'})
def request_access(request, adopter_id):
    adopter = Adopter.objects.update_or_create(
        pk=adopter_id,
        defaults={'requested_access': True}
    )[0]

    access_requested(adopter)
    confirm_access_request(adopter)
    return redirect('calendar')


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def allow_access(request, adopter_id):
    adopter = Adopter.objects.update_or_create(
        pk=adopter_id,
        defaults={
            'adoption_complete': False,
            'requested_access': False,
            'requested_surrender': False
        }
    )[0]

    access_restored(adopter)
    return redirect('edit_adopter', adopter.id, alert=True)


# REFACTORED
@authenticated_user
@allowed_users(allowed_roles={'adopter'})
def surrender_form(request, adopter_id):
    form = SurrenderForm(request.POST or None)
    
    if form.is_valid():
        adopter = Adopter.objects.update_or_create(
            pk=adopter_id,
            defaults={'requested_surrender': True}
        )[0]
        data = form.cleaned_data
        surrender_emails(adopter, data)        
        return redirect('calendar')
    else:
        form = SurrenderForm(request.POST or None)

    context = {
        'form': form,
        'form_instructions': "Please fill out this form to the best of your ability.",
        'page_header': "Surrender Form",
        'page_title': "Surrender Form",
    }

    return render(request, "appt_calendar/render_form.html", context)
