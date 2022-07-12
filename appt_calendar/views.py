from django.shortcuts import render, get_object_or_404, redirect
import datetime, time, sys
from schedule_template.models import Daily_Schedule, TimeslotTemplate, AppointmentTemplate, SystemSettings
from .models import *
from adopter.models import Adopter
from .forms import *
from adopter.forms import *
from email_mgr.email_sender import *
from .date_time_strings import *
from .appointment_manager import *
from dashboard.views import generate_calendar as gc
from django.contrib.auth.models import Group, User
from dashboard.decorators import *
from reportlab.pdfgen import canvas
from django.http import HttpResponseRedirect

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

def set_alert_date_greeter(request, adopter_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    adopter = Adopter.objects.get(pk=adopter_id)

    adopter.alert_date = date
    adopter.save()

    today = datetime.date.today()

    alert_date_set(adopter, date)

    return redirect('calendar_date', today.year, today.month, today.day)

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
    full_name = adopter.full_name()

    if source == 'edit' or 'mgmt' in source:
        action = "Scheduling"
    else:
        action = 'Rescheduling'

    context = {
        "full_name": full_name,
        "adopter": adopter,
        "appt": old_appt,
        "source": source,
        "action": action,
        'page_title': "Reschedule {0}".format(full_name),
    }

    calendar = gc(request.user, 'reschedule', None, date_year, date_month, date_day)

    context.update(calendar)

    return render(request, "appt_calendar/calendar_greeter_reschedule.html/", context)

def book_appointment(request, appt_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    adopter = request.user.adopter

    if appt.available == False and appt.adopter != adopter:

        context = {
            'adopter': adopter,
            'page_title': "Appointment Not Available",
        }

        return render(request, "appt_calendar/appt_not_available.html", context)

    else:
        form = BookAppointmentForm(request.POST or None, instance=appt)
        adopter_form = AdopterPreferenceForm(request.POST or None, instance=adopter)

        if form.is_valid():
            form.save()
            adopter_form.save()

            print(request.POST)

            # try:
            #     questions = dict(request.POST)['outstanding_questions'][0]
            #
            #     if questions != "":
            #         questions_msg(adopter, appt, questions)
            # except Exception as e:
            #     exception_type, exception_object, exception_traceback = sys.exc_info()
            #     filename = exception_traceback.tb_frame.f_code.co_filename
            #     line_number = exception_traceback.tb_lineno
            #
            #     print("Exception type: ", exception_type)
            #     print("File name: ", filename)
            #     print("Line number: ", line_number)

            adopter.has_current_appt = True
            adopter.save()

            appt.adopter = adopter
            appt.delist()

            confirm_etemp(adopter, appt)

            if short_notice(appt):
                appt.mark_short_notice()

                try:
                    sn_obj = ShortNotice.objects.get(date = appt.date, adopter = adopter)
                    print(sn_obj.id)
                    sn_obj.prev_appt, sn_obj.current_appt = None, appt
                    sn_obj.sn_status = "1"
                    sn_obj.save()
                except Exception as e:
                    print('e', e)
                    sn_obj = ShortNotice.objects.create(adopter = adopter, current_appt = appt, prev_appt = None, date = appt.date, sn_status = "1")

                notify_adoptions_add(adopter, appt)

            return redirect('calendar')
        else:

            form = BookAppointmentForm(request.POST or None, instance=appt, initial={'adopter': adopter})
            adopter_form = AdopterPreferenceForm(request.POST or None, instance=adopter)

        context = {
            'form': form,
            'adopter_form': adopter_form,
            'adopter': adopter,
            'page_title': "Book Appointment",
        }

        return render(request, "appt_calendar/bookappt.html", context)

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
        'page_title': "Jump To Date",
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
        'page_title': "Jump To Date",
    }

    return render(request, "appt_calendar/jump_to_date.html", context)

def calendar_date(request, date_year, date_month, date_day):
    try:
        user_groups = set(group.name for group in request.user.groups.all().iterator())
    except:
        user_groups = set()

    context = gc(request.user, 'full', None, date_year, date_month, date_day)

    if 'adopter' in user_groups:
        # context['role'] = 'adopter'
        try:
            current_appt = Appointment.objects.filter(adopter=request.user.adopter).latest('id') #.exclude(date__lt = today)
            current_appt_str = current_appt.date_and_time_string()
        except:
            current_appt = None
            current_appt_str = None

        adopter_context = {
            'current_appt': current_appt,
            'current_appt_str': current_appt_str,
            'page_title': "Calendar",
        }

        context.update(adopter_context)

    return render(request, "appt_calendar/calendar_test_harness.html", context)

def calendar_date_appt(request, date_year, date_month, date_day, appt_id):
    try:
        user_groups = set(group.name for group in request.user.groups.all().iterator())
    except:
        user_groups = set()

    context = gc(request.user, 'full', None, date_year, date_month, date_day)

    try:
        appt = Appointment.objects.get(pk=appt_id)
        ts_query = Timeslot.objects.get(appointments__id__exact=appt.id)

        redirect_context = {
            'go_to_div': "ts{0}".format(ts_query.id),
        }

        context.update(redirect_context)
    except:
        pass

    if 'adopter' in user_groups:
        # context['role'] = 'adopter'
        try:
            current_appt = Appointment.objects.filter(adopter=request.user.adopter).latest('id') #.exclude(date__lt = today)
            current_appt_str = current_appt.date_and_time_string()
        except:
            current_appt = None
            current_appt_str = None

        adopter_context = {
            'current_appt': current_appt,
            'current_appt_str': current_appt_str,
            'page_title': "Calendar",
        }

        context.update(adopter_context)

    return render(request, "appt_calendar/calendar_test_harness.html", context)

def calendar_date_ts(request, date_year, date_month, date_day, ts_id):
    try:
        user_groups = set(group.name for group in request.user.groups.all().iterator())
    except:
        user_groups = set()

    context = gc(request.user, 'full', None, date_year, date_month, date_day)

    try:
        ts_query = Timeslot.objects.get(pk=ts_id)

        redirect_context = {
            'go_to_div': "ts{0}".format(ts_query.id),
        }

        context.update(redirect_context)
    except:
        pass

    if 'adopter' in user_groups:
        # context['role'] = 'adopter'
        try:
            current_appt = Appointment.objects.filter(adopter=request.user.adopter).latest('id') #.exclude(date__lt = today)
            current_appt_str = current_appt.date_and_time_string()
        except:
            current_appt = None
            current_appt_str = None

        adopter_context = {
            'current_appt': current_appt,
            'current_appt_str': current_appt_str,
            'page_title': "Calendar",
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
        'page_title': "Calendar",
    }

    context.update(calendar)

    return render(request, "appt_calendar/paperwork_calendar.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def calendar_print(request, date_year, date_month, date_day):
    context = gc(request.user, 'full', None, date_year, date_month, date_day)

    context['page_title'] = "Print Calendar"

    return render(request, "appt_calendar/calendar_print.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def report_print(request, date_year, date_month, date_day):
    context = gc(request.user, 'full', None, date_year, date_month, date_day)

    context['page_title'] = "Daily Report"

    return render(request, "appt_calendar/daily_report_print.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def daily_report_all_appts(request, date_year, date_month, date_day):
    return redirect('daily_report_adopted_chosen_fta')
    context = gc(request.user, 'full', None, date_year, date_month, date_day)

    context['page_title'] = "All Appointments Report"

    return render(request, "appt_calendar/daily_report_all_appts.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def daily_reports_home(request):
    date = datetime.date.today()

    return redirect('daily_report_adopted_chosen_fta', date.year, date.month, date.day)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def chosen_board(request):
    today = datetime.date.today()
    appointments = [appt for appt in Appointment.objects.filter(outcome__in = ["3", "7", "8", "9", "10"], paperwork_complete=False)]

    context = {
        "today": today,
        "appointments": appointments,
        'page_title': "Chosen Board",
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
def cb_update_status(request, appt_id, outcome):
    appt = Appointment.objects.get(pk=appt_id)

    appt.outcome = outcome
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
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def daily_report_adopted_chosen_fta(request, date_year, date_month, date_day):
    context = gc(request.user, 'full', None, date_year, date_month, date_day)

    return render(request, "appt_calendar/daily_report_adopted_chosen_fta.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'greeter'})
def send_followup(request, appt_id, date_year, date_month, date_day, host):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)

    appt.outcome = "5"
    appt.comm_followup = True
    appt.save()

    adopter = appt.adopter

    if host == 0:
        follow_up(adopter)
    else:
        follow_up_w_host(adopter)

    adopter.has_current_appt = False
    adopter.visits_to_date += 1
    adopter.save()

    return redirect('calendar_date_appt', date.year, date.month, date.day, appt.id)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def delete_timeslot(request, date_year, date_month, date_day, timeslot_id):
    date = datetime.date(date_year, date_month, date_day)
    deleted_timeslot = get_object_or_404(Timeslot, pk=timeslot_id)
    deleted_timeslot.delete()

    return redirect('calendar_date', date.year, date.month, date.day)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_daily_announcement(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    form = DailyAnnouncementForm(request.POST or None, initial = {'date': date})

    if form.is_valid():
        form.save()
        return redirect('calendar_date', date.year, date.month, date.day)

    else:
        form = DailyAnnouncementForm(request.POST or None, initial = {'date': date})

    context = {
        'form': form,
        'date': date,
        'title': "Add Calendar Note for {0}".format(date_str(date)),
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_daily_announcement(request, announcement_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    announcement = DailyAnnouncement.objects.get(pk = announcement_id)
    form = DailyAnnouncementForm(request.POST or None, instance=announcement)

    if form.is_valid():
        form.save()
        return redirect('calendar_date', date.year, date.month, date.day)

    else:
        form = DailyAnnouncementForm(request.POST or None, instance=announcement)

    context = {
        'form': form,
        'date': date,
        'title': "Edit Calendar Note for {0}".format(date_str(date)),
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def add_internal_announcement(request, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    form = InternalAnnouncementForm(request.POST or None, initial = {'date': date})

    if form.is_valid():
        form.save()
        return redirect('calendar_date', date.year, date.month, date.day)

    else:
        form = InternalAnnouncementForm(request.POST or None, initial = {'date': date})

    context = {
        'form': form,
        'date': date,
        'title': "Add Calendar Note for {0}".format(date_str(date)),
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_internal_announcement(request, announcement_id, date_year, date_month, date_day):
    date = datetime.date(date_year, date_month, date_day)
    announcement = InternalAnnouncement.objects.get(pk = announcement_id)
    form = InternalAnnouncementForm(request.POST or None, instance=announcement)

    if form.is_valid():
        form.save()
        return redirect('calendar_date', date.year, date.month, date.day)

    else:
        form = InternalAnnouncementForm(request.POST or None, instance=announcement)

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
            appt.delist()

        if appt.adopter is not None:

            adopter = appt.adopter
            adopter.has_current_appt = True
            adopter.save()

            appt.delist()

            if short_notice(appt):
                sn_obj = ShortNotice.objects.create(adopter = adopter, dog = appt.dog, current_appt = appt, date = appt.date, sn_status = "1")
                appt.mark_short_notice()
                notify_adoptions_add(adopter, appt)

            if appt.appt_type in ["1", "2", "3"]:
                return redirect('contact_adopter', appt.id, date_year, date_month, date_day, 'confirm_appt')

        return redirect('calendar_date_appt', date.year, date.month, date.day, appt.id)
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
def add_followup_appointment(request, adopter_id, date_year, date_month, date_day, timeslot_id):
    date = datetime.date(date_year, date_month, date_day)

    timeslot = Timeslot.objects.get(pk=timeslot_id)
    appt = Appointment.objects.create(date = date, time = timeslot.time)

    timeslot.appointments.add(appt)

    return redirect('adopter_reschedule', adopter_id, appt.id, date_year, date_month, date_day, 'edit')

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

    form = AppointmentModelFormPrefilled(
        request.POST or None,
        initial = {
            'date': date,
            'time': timeslot.time,
            'appt_type': paperwork_appt_type,
            'adopter': original_appt.adopter,
            'available': False,
            'published': False,
            'dog': original_appt.dog
        }
    )

    if form.is_valid():
        form.save()
        appt = Appointment.objects.latest('id')
        timeslot.appointments.add(appt)

        original_appt.outcome = "8"
        original_appt.save()

        if appt.adopter is not None:

            adopter = appt.adopter
            adopter.has_current_appt = False
            adopter.save()

            appt.delist()

            adoption_paperwork(adopter, appt, original_appt.heartworm)

            if short_notice(appt):
                appt.mark_short_notice()
                sn_obj = ShortNotice.objects.create(dog = appt.dog, current_appt = appt, date = appt.date, sn_status = "1")
                notify_adoptions_paperwork(appt.adopter, appt)

        return redirect('chosen_board')
    else:
        form = AppointmentModelFormPrefilled(initial={'date': date, 'time': timeslot.time, 'appt_type': paperwork_appt_type, 'adopter': original_appt.adopter, 'available': False, 'published': False, 'dog': original_appt.dog})

    context = {
        'form': form,
        'date': date,
        'timeslot': timeslot,
        'title': "Add Paperwork Appointment",
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

def short_notice(appt):
    is_today = appt.date == datetime.date.today()
    is_tomorrow = appt.date == datetime.date.today() + datetime.timedelta(days=1)
    booked_after_close = datetime.datetime.now().time() > datetime.time(16,00)

    if is_today or (is_tomorrow and booked_after_close):
        return True

    return False

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser', 'adopter'})
def edit_appointment(request, date_year, date_month, date_day, appt_id):
    try:
        user_groups = set(group.name for group in request.user.groups.all().iterator())
    except:
        user_groups = set()

    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    original_adopter = appt.adopter

    if user_groups == {'adopter'}:
        form = EditAppointmentForm(request.POST or None, instance=appt,)
        adopter_form = AdopterPreferenceForm(request.POST or None, instance=original_adopter)
    else:
        print(appt.adopter)
        if appt.adopter is not None:
            form = AppointmentModelFormPrefilledEdit(request.POST or None, instance=appt)
        else:
            form = AppointmentModelFormPrefilled(request.POST or None, instance=appt)
        adopter_form = None

    if appt.adopter is not None:
        current_email = appt.adopter.primary_email
    else:
        current_email = None

    if form.is_valid():
        form.save()

        if adopter_form:
            adopter_form.save()

        if short_notice(appt):
            if short_notice(appt):
                try:
                    sn_obj = ShortNotice.objects.get(date = appt.date, adopter = appt.adopter, dog = appt.dog)
                    print(sn_obj.id)
                    sn_obj.prev_appt, sn_obj.current_appt = sn_obj.current_appt, None
                    sn_obj.sn_status = "1"
                    sn_obj.save()
                except Exception as e:
                    print('e', e)
                    appt.mark_short_notice()
                    sn_obj = ShortNotice.objects.create(adopter = appt.adopter, dog=appt.dog, current_appt = appt, date = appt.date, sn_status = "1")
                    notify_adoptions_add(appt.adopter, appt)

        try:
            post_save_email = appt.adopter.primary_email
        except:
            post_save_email = None
        if appt.adopter is not None:
            if appt.appt_type in ["1", "2", "3"]:
                if original_adopter not in [None, appt.adopter]:
                    cancel(original_adopter, appt)

                # if short_notice(appt) and appt.adopter not in [None, original_adopter]:
                #     appt.mark_short_notice()
                #     sn_obj = ShortNotice.objects.create(adopter = appt.adopter, dog = appt.dog, current_appt = appt, date = appt.date, sn_status = "1")
                #     notify_adoptions_add(appt.adopter, appt)

                appt.adopter.has_current_appt = True
                appt.adopter.save()

            appt.delist()

        return redirect('calendar_date_appt', date.year, date.month, date.day, appt.id)
    else:
        if user_groups == {'adopter'}:
            form = EditAppointmentForm(request.POST or None, instance=appt,)
            adopter_form = AdopterPreferenceForm(request.POST or None, instance=original_adopter)
        else:
            if appt.adopter is not None:
                form = AppointmentModelFormPrefilledEdit(request.POST or None, instance=appt)
            else:
                form = AppointmentModelFormPrefilled(request.POST or None, instance=appt)
            adopter_form = None

    context = {
        'form': form,
        'adopter_form': adopter_form,
        'title': "Edit Appointment",
        'adopter': appt.adopter,
    }

    return render(request, "appt_calendar/add_edit_appt.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_appointment_from_mgmt(request, date_year, date_month, date_day, appt_id):
    try:
        user_groups = set(group.name for group in request.user.groups.all().iterator())
    except:
        user_groups = set()

    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    original_adopter = appt.adopter

    if user_groups == {'adopter'}:
        form = EditAppointmentForm(request.POST or None, instance=appt)
    else:
        if appt.adopter is not None:
            form = AppointmentModelFormPrefilledEdit(request.POST or None, instance=appt)
        else:
            form = AppointmentModelFormPrefilled(request.POST or None, instance=appt)

    if appt.adopter is not None:
        current_email = appt.adopter.primary_email
    else:
        current_email = None

    if form.is_valid():
        form.save()

        try:
            post_save_email = appt.adopter.primary_email
        except:
            post_save_email = None
        if appt.adopter is not None:
            if appt.appt_type in ["1", "2", "3"]:
                if original_adopter not in [None, appt.adopter]:
                    cancel(original_adopter, appt)

                if short_notice(appt) and appt.adopter not in [None, original_adopter]:
                    appt.mark_short_notice()
                    sn_obj = ShortNotice.objects.create(adopter = appt.adopter, current_appt = appt, date = appt.date, sn_status = "1")
                    notify_adoptions_add(appt.adopter, appt)

                appt.adopter.has_current_appt = True
                appt.adopter.save()

            appt.delist()

            print('hey')
            return redirect('contact_adopter', appt_id, date_year, date_month, date_day, 'confirm_appt')

        return redirect('edit_adopter', original_adopter.id)
    else:
        if user_groups == {'adopter'}:
            form = EditAppointmentForm(request.POST or None, instance=appt)
        else:
            if appt.adopter is not None:
                form = AppointmentModelFormPrefilledEdit(request.POST or None, instance=appt)
            else:
                form = AppointmentModelFormPrefilled(request.POST or None, instance=appt)

    context = {
        'form': form,
        'title': "Edit Appointment",
        'adopter': appt.adopter,
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

        adopter = appt.adopter

        adopter.has_current_appt = False

        if appt.outcome == "5":
            adopter.visits_to_date += 1
            follow_up(adopter)
        elif appt.outcome in ["2", "3", "4"]:
            adopter.visits_to_date = 0
            #
            # if appt.outcome == "3":
            #     chosen(adopter, appt)

        adopter.save()

        return redirect('calendar')

    else:
        form = ApptOutcomeForm(request.POST or None, instance=appt)

    context = {
        'form': form,
        'page_title': "Enter Decision",
    }

    return render(request, "appt_calendar/enter_decision_form.html", context)

def remove_adopter(request, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    appt = Appointment.objects.get(pk=appt_id)
    adopter = appt.adopter

    if appt.appt_type in ["1", "2", "3"]:
        cancel(adopter, appt)

    adopter.has_current_appt = False
    adopter.save()

    appt.reset()

    if short_notice(appt):
        try:
            sn_obj = ShortNotice.objects.get(date = appt.date, adopter = adopter)
            print(sn_obj.id)
            sn_obj.prev_appt, sn_obj.current_appt = sn_obj.current_appt, None
            sn_obj.sn_status = "2"
            sn_obj.save()
        except Exception as e:
            print('e', e)
            sn_obj = ShortNotice.objects.create(adopter = adopter, prev_appt = appt, date = appt.date, sn_status = "2")

        notify_adoptions_cancel(appt, adopter)

    if get_groups(request.user) == {'adopter'}:
        appt_str = appt.date_and_time_string()

        context = {
            'adopter': adopter,
            'appt_str': appt_str,
            'page_title': "Appointment Canceled",
        }

        return render(request, "appt_calendar/adopter_self_cancel.html", context)

    else:
        return redirect('calendar_date_appt', date.year, date.month, date.day, appt.id)

def adopter_reschedule(request, adopter_id, appt_id, date_year, date_month, date_day, source):
    adopter = Adopter.objects.get(pk=adopter_id)
    date = datetime.date(date_year, date_month, date_day)
    appt_set = Appointment.objects.filter(adopter=adopter.id).exclude(date__lt = datetime.date.today())
    user_groups = get_groups(request.user)

    try:
        current_appt = [appt for appt in Appointment.objects.filter(adopter=adopter.id).exclude(date__lt = datetime.date.today())][0]
    except:
        current_appt = None

    new_appt = Appointment.objects.get(pk=appt_id)

    print("Attempting to reschedule {0} to appointment {1}".format(adopter.full_name(), new_appt.id))

    if new_appt.available == False and new_appt.adopter != adopter:
        context = {
            'adopter': adopter,
            'appt': Appointment.objects.get(pk=appt_id),
            'date': date,
            'page_title': "Appointment Not Available",
        }

        print("Aborted, appointment was already booked")

        return render(request, "appt_calendar/appt_not_available.html", context)
    else:
        try:
            new_appt.internal_notes = current_appt.internal_notes
            new_appt.adopter_notes = current_appt.adopter_notes
            new_appt.bringing_dog = current_appt.bringing_dog
            new_appt.has_cat = current_appt.has_cat
            new_appt.mobility = current_appt.mobility
            print("Appointment details carried")

            if source == "followup":
                new_appt.appt_type = current_appt.appt_type
                print("Appointment type copied")

        except:
            pass

        if user_groups == {"adopter"} or ("admin" in user_groups and source == "calendar"):
            print("Resetting appointment {0}, removing {1}".format(current_appt.id, adopter.full_name()))
            current_appt.reset()
            current_appt.save()

        new_appt.adopter = adopter
        adopter.has_current_appt = True

        adopter.save()
        new_appt.save()

        if user_groups == {"adopter"}:
            new_appt.delist()

            reschedule(adopter, new_appt)

            if short_notice(current_appt) and short_notice(new_appt):
                new_appt.mark_short_notice()

                try:
                    sn_obj = ShortNotice.objects.get(date = new_appt.date, adopter = adopter)
                    print(sn_obj.id)
                    sn_obj.prev_appt, sn_obj.current_appt = current_appt, new_appt
                    sn_obj.sn_status = "3"
                    sn_obj.save()
                except Exception as e:
                    print('e', e)
                    sn_obj = ShortNotice.objects.create(adopter = adopter, prev_appt = current_appt, current_appt = new_appt, date = new_appt.date, sn_status = "3")

                notify_adoptions_time_change(adopter, current_appt, new_appt)

            elif short_notice(current_appt):

                try:
                    sn_obj = ShortNotice.objects.get(date = current_appt.date, adopter = adopter)
                    print(sn_obj.id)
                    sn_obj.prev_appt, sn_obj.current_appt = sn_obj.current_appt, None
                    sn_obj.sn_status = "2"
                    sn_obj.save()
                except Exception as e:
                    print('e', e)
                    sn_obj = ShortNotice.objects.create(adopter = adopter, prev_appt = current_appt, date = current_appt.date, sn_status = "2")

                notify_adoptions_reschedule_cancel(adopter, current_appt, new_appt)

            elif short_notice(new_appt):
                new_appt.mark_short_notice()

                try:
                    sn_obj = ShortNotice.objects.get(date = new_appt.date, adopter = adopter)
                    print(sn_obj.id)
                    sn_obj.prev_appt, sn_obj.current_appt = None, new_appt
                    sn_obj.sn_status = "1"
                    sn_obj.save()
                except Exception as e:
                    print('e', e)
                    sn_obj = ShortNotice.objects.create(adopter = adopter, current_appt = new_appt, prev_appt = None, date = new_appt.date, sn_status = "1")

                notify_adoptions_reschedule_add(adopter, current_appt, new_appt)

            return redirect("calendar_date_appt", date_year, date_month, date_day, new_appt.id)

        else:
            today = datetime.date.today()

            if ('greeter' in user_groups and 'admin' not in user_groups) or ('admin' in user_groups and source == "followup"):
                try:
                    current_appt.outcome = "5"
                    current_appt.save()
                    adopter.visits_to_date += 1
                    adopter.has_current_appt = True
                    adopter.save()

                    new_appt.delist()

                    greeter_reschedule_email(adopter, new_appt)
                    return redirect("calendar_date", today.year, today.month, today.day)
                except:
                    pass
            elif 'admin' in user_groups:

                # try:
                #     if short_notice(current_appt) and short_notice(new_appt):
                #         new_appt.mark_short_notice()
                #         notify_adoptions_time_change(adopter, current_appt, new_appt)
                #     elif short_notice(current_appt):
                #         notify_adoptions_reschedule_cancel(adopter, current_appt, new_appt)
                # except:
                #     if short_notice(new_appt):
                #         new_appt.mark_short_notice()
                #         notify_adoptions_reschedule_add(adopter, current_appt, new_appt)

                try:
                    if short_notice(current_appt) and short_notice(new_appt):
                        new_appt.mark_short_notice()

                        try:
                            sn_obj = ShortNotice.objects.get(date = new_appt.date, adopter = adopter)
                            print(sn_obj.id)
                            sn_obj.prev_appt, sn_obj.current_appt = current_appt, new_appt
                            sn_obj.sn_status = "3"
                            sn_obj.save()
                        except Exception as e:
                            print('e', e)
                            sn_obj = ShortNotice.objects.create(adopter = adopter, prev_appt = current_appt, current_appt = new_appt, date = new_appt.date, sn_status = "3")

                        notify_adoptions_time_change(adopter, current_appt, new_appt)

                    elif short_notice(current_appt):

                        try:
                            sn_obj = ShortNotice.objects.get(date = current_appt.date, adopter = adopter)
                            print(sn_obj.id)
                            sn_obj.prev_appt, sn_obj.current_appt = sn_obj.current_appt, None
                            sn_obj.sn_status = "2"
                            sn_obj.save()
                        except Exception as e:
                            print('e', e)
                            sn_obj = ShortNotice.objects.create(adopter = adopter, prev_appt = current_appt, date = current_appt.date, sn_status = "2")

                        notify_adoptions_reschedule_cancel(adopter, current_appt, new_appt)
                except:
                    if short_notice(new_appt):
                        new_appt.mark_short_notice()

                        try:
                            sn_obj = ShortNotice.objects.get(date = new_appt.date, adopter = adopter)
                            print(sn_obj.id)
                            sn_obj.prev_appt, sn_obj.current_appt = None, new_appt
                            sn_obj.sn_status = "1"
                            sn_obj.save()
                        except Exception as e:
                            print('e', e)
                            sn_obj = ShortNotice.objects.create(adopter = adopter, current_appt = new_appt, prev_appt = None, date = new_appt.date, sn_status = "1")

                        notify_adoptions_reschedule_add(adopter, current_appt, new_appt)

                adopter.has_current_appt = True
                adopter.save()

                new_appt.delist()

                if source == "edit":
                    # confirm_etemp(adopter, new_appt)
                    # return redirect('edit_adopter', adopter.id)
                    return redirect('edit_cal_appointment_mgmt', new_appt.id, new_appt.date.year, new_appt.date.month, new_appt.date.day)
                else:
                    reschedule(adopter, new_appt)
                    return redirect("calendar_date", today.year, today.month, today.day)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def delete_appointment(request, date_year, date_month, date_day, appt_id):
    date = datetime.date(date_year, date_month, date_day)
    deleted_appt = get_object_or_404(Appointment, pk=appt_id)
    ts_query = Timeslot.objects.get(appointments__id__exact=deleted_appt.id)

    if deleted_appt.adopter:
        cancel(deleted_appt.adopter, deleted_appt)

        deleted_appt.adopter.has_current_appt = False
        deleted_appt.adopter.save()

        deleted_appt.reset()

    deleted_appt.delete()

    return redirect('calendar_date_ts', date.year, date.month, date.day, ts_query.id)

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

        return redirect('calendar_date_ts', date.year, date.month, date.day, new_ts.id)
    else:
        form = NewTimeslotModelForm(request.POST or None, initial={'daypart': "1"})

    context = {
        'form': form,
        'date': date,
        'page_title': "Add Timeslot",
    }

    return render(request, "appt_calendar/new_timeslot_form.html", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def toggle_lock(request, appt_id, date_year, date_month, date_day):
    appt = Appointment.objects.get(pk=appt_id)
    appt.locked = not appt.locked
    appt.save()

    return redirect('calendar_date_appt', date_year, date_month, date_day, appt_id)
    # return redirect('calendar_date', date_year, date_month, date_day)
    # return HttpResponseRedirect('?next=calendar/{0}/{1}/{2}/#{3}'.format(date_year, date_month, date_day, appt_id))

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def toggle_all(request, date_year, date_month, date_day, lock):
    date = datetime.date(date_year, date_month, date_day)
    appts = list(Appointment.objects.filter(date = date, appt_type__in = ["1", "2", "3"]))

    for appt in appts:
        appt.locked = bool(lock)
        appt.save()

    return redirect('calendar_date', date_year, date_month, date_day)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def toggle_time(request, timeslot_id, date_year, date_month, date_day, lock):
    date = datetime.date(date_year, date_month, date_day)
    timeslot = Timeslot.objects.get(pk=timeslot_id)
    appts = list(timeslot.appointments.filter(date = date, time = timeslot.time, appt_type__in = ["1", "2", "3"]))

    for appt in appts:
        appt.locked = bool(lock)
        appt.save()

    return redirect('calendar_date_ts', date_year, date_month, date_day, timeslot.id)

# @authenticated_user
# @allowed_users(allowed_roles={'admin', 'superuser'})
# def gen_applications(request, date_year, date_month, date_day):
#     date = datetime.date(date_year, date_month, date_day)
#     filename = 'Applications{0}{1}{2}.pdf'.format(date_year, date_month, date_day)
#     pdf = canvas.Canvas(filename)
#
#     pdf.setTitle('Applications for {0}'.format(date_str(date)))
#     pdf.save()
#
#     return redirect('calendar_date', date_year, date_month, date_day)
