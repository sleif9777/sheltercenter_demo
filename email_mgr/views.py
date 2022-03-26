from django.shortcuts import render, get_object_or_404, redirect
import datetime, time
from .forms import *
from io import StringIO
from html.parser import HTMLParser
from .email_sender import *

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def email_home(request):

    return render(request, "email_mgr/email_home.html/")

def add_email_template(request):

    form = EmailTemplateForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data

        plain = strip_tags(data['text'])

        new_template = EmailTemplate.objects.create(template_name = data['template_name'], text = data['text'], plain = plain)

        send_email(plain, data['text'], 'sheltercenterdev@gmail.com', data['template_name'], 'sheltercenterdev@gmail.com')

        return redirect('email_home')
    else:
        form = EmailTemplateForm(request.POST or None)

    context = {
        'form': form,
    }

    return render(request, "email_mgr/add_template.html/", context)

# def add_timeslot(request, dow_id):
#     dow = Daily_Schedule.objects.get(pk=dow_id)
#
#     form = NewTimeslotModelForm(request.POST or None, initial={'daypart': "1"})
#
#     if form.is_valid():
#         data = form.cleaned_data
#         hour = int(data['hour'])
#         print(hour)
#         minute = int(data['minute'])
#         daypart = data['daypart']
#
#         if daypart == "1" and hour < 12:
#             hour += 12
#
#         new_ts = TimeslotTemplate.objects.create(day_of_week = dow.day_of_week, time = datetime.time(hour, minute))
#         dow.timeslots.add(TimeslotTemplate.objects.latest('id'))
#
#         return redirect('daily', dow_id)
#     else:
#         form = NewTimeslotModelForm(request.POST or None, initial={'daypart': "1"})
#
#     context = {
#         'form': form,
#         'dow': dow,
#     }
#
#     return render(request, "schedule_template/timeslot_form.html", context)
