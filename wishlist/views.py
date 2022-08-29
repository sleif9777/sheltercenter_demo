import datetime
import os
import requests

from django.contrib.auth.models import Group, User
from django.shortcuts import render

from .forms import *
from .models import *
from dashboard.decorators import *

def get_and_update_dogs():
    headers = {
        'X-Api-Key': os.environ.get('SHELTERLUV_API_KEY'),
    }

    has_more = True
    offset = 0
    dogs = []
    previous_available_dogs = [dog for dog in Dog.objects.filter(shelterluv_status="Available for Adoption")]
    current_available_dogs = []

    # get all currently available_dogs
    while has_more:
        dogs_request = requests.get('https://www.shelterluv.com/api/v1/animals?offset={0}&status_type=publishable'.format(offset), headers=headers).json()
        dogs += dogs_request['animals']
        offset += 100
        has_more = dogs_request['has_more']

    # try to call dog, if not existing, create object and save
    for dog in dogs:
        updated_values = {'info': dog, 'shelterluv_status': dog['Status'], 'name': dog['Name']}

        dog_obj = Dog.objects.update_or_create(shelterluv_id=dog['Internal-ID'], defaults = updated_values)
        current_available_dogs += [dog_obj[0]]

    # determine which dogs were recently removed from website and update status
    recent_delisted = [dog for dog in previous_available_dogs if dog not in current_available_dogs]

    for dog in recent_delisted:
        dog.shelterluv_status = 'Delisted' #dog_req['Status']
        dog.save()
#
# def check_for_updated_status():
#     available_dogs = Dog.objects.get(shelterluv_status="Available for Adoption")
#
#     for dog in available_dogs:
#         update_request = requests.get('https://www.shelterluv.com/api/v1/animals?offset={0}&status_type=publishable'.format(offset), params=params, headers=headers).json()

@authenticated_user
@allowed_users(allowed_roles={'superuser'})
def display_list(request):
    get_and_update_dogs()

    all_available_dogs = [dog for dog in Dog.objects.filter(shelterluv_status = 'Available for Adoption').order_by('name')]

    if request.method == "POST":
        form_data = dict(request.POST)
        del form_data['csrfmiddlewaretoken']

        form_data = dict([(k, v) for k, v in form_data.items() if v[0] != ""])

        print(form_data)

        for dog in Dog.objects.filter(appt_only=True):
            if dog.shelterluv_id not in form_data.keys():
                dog.appt_only = False
                dog.save()

        for id in form_data.keys():
            dog = Dog.objects.get(shelterluv_id=id[:-5])
            dog.offsite = True

            if '-appt' in id:
                dog.appt_only = True
            elif '-host' in id:
                date_string = form_data[id][0]
                dog.host_date = datetime.date(int(date_string[:4]), int(date_string[5:7]), int(date_string[8:]))
            elif '-fstr' in id:
                date_string = form_data[id][0]
                dog.foster_date = datetime.date(int(date_string[:4]), int(date_string[5:7]), int(date_string[8:]))

            dog.save()

        return redirect('calendar')

    context = {
        'all_available_dogs': all_available_dogs,
    }

    return render(request, "wishlist/list.html", context)
