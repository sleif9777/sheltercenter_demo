import json
import operator
import os
import requests

from django.contrib.auth.models import Group, User
from django.shortcuts import render

from .models import *
from dashboard.decorators import *


def get_groups(user_obj):
    try:
        user_groups = set(group.name for group in user_obj.groups.all().iterator())
    except:
        user_groups = set()

    return user_groups


def update_from_shelterluv():
    dogs = []
    has_more = True
    headers = {'X-Api-Key': os.environ.get('SHELTERLUV_API_KEY')}
    offset = 0

    while has_more:
        request_address = 'https://www.shelterluv.com/api/v1/animals?offset={0}&status_type=publishable'.format(offset)
        dogs_request = requests.get(request_address, headers=headers).json()
        dogs += dogs_request['animals']
        offset += 100
        has_more = dogs_request['has_more']

    for dog_json in dogs:        
        DogProfile.objects.update_or_create(
            shelterluv_id = dog_json['Internal-ID'],
            defaults={
                'name': dog_json['Name'],
                'info': dog_json,
                'shelterluv_status': dog_json['Status']
            }
        )


def get_and_update_dogs():
    update_from_shelterluv()
    remove_expired_dates()


def get_all_available_dogs():
    all_available_dogs = [dog for dog in DogProfile.objects.filter(shelterluv_status='Available for Adoption')]
    all_available_dogs = sorted(all_available_dogs, key=operator.attrgetter('name'))

    return all_available_dogs


def remove_expired_dates():
    today = datetime.datetime.today()
    default_date = datetime.date(2000, 1, 1)
    shifted_date = datetime.date(2000, 1, 2) # to exclude true 1/1/2000 default
    
    for dog in DogProfile.objects.filter(
            host_date__range=(shifted_date, today)):
        print('remove_expired_dates host', dog.name)
        dog.host_date = default_date
        dog.offsite = True if dog.appt_only else False
        dog.save()

    for dog in DogProfile.objects.filter(
            foster_date__range=(shifted_date, today)):
        print('remove_expired_dates foster', dog.name)
        dog.foster_date = default_date
        dog.offsite = True if dog.appt_only else False
        dog.save()


def get_date_from_form_data(data):
    year = int(data[:4])
    month = int(data[5:7])
    day = int(data[8:])

    return year, month, day


@authenticated_user
@allowed_users(allowed_roles={'superuser', 'admin', 'adopter'})
def display_list(request):
    user_groups = get_groups(request.user)

    if 'adopter' in user_groups:
        return redirect('display_list_adopter')
    else:
        return redirect('display_list_admin')


@authenticated_user
@allowed_users(allowed_roles={'adopter'})
def display_list_adopter(request):
    user_wishlist = request.user.adopter.wishlist

    if request.method == "POST":
        form_data = dict(request.POST)
        del form_data['csrfmiddlewaretoken']

        ids_in_wishlist = [dog.shelterluv_id for dog in user_wishlist.iterator()]

        for id in ids_in_wishlist:
            if id not in form_data:
                user_wishlist.remove(DogProfile.objects.get(shelterluv_id=id))

        for id in form_data:
            user_wishlist.add(DogProfile.objects.get(shelterluv_id=id))

    all_available_dogs = get_all_available_dogs()
    user_wishlist_arr = [dog for dog in user_wishlist.iterator()]
    other_available_dogs = [dog for dog in all_available_dogs if dog not in user_wishlist_arr]
 
    context = {
        'other_available_dogs': other_available_dogs,
        'user_wishlist': user_wishlist_arr,
    }

    return render(request, "wishlist/list_adopter.html", context)


def update_dog_from_form_data(id, form_data):
    dog = DogProfile.objects.get(shelterluv_id=id[:-5])
    dog.offsite = True

    if '-appt' in id:
        dog.appt_only = True
    else:
        year, month, day = get_date_from_form_data(form_data[0])
        if '-host' in id:
            dog.host_date = datetime.date(year, month, day)
        elif '-fstr' in id:
            dog.foster_date = datetime.date(year, month, day)

    dog.save()


@authenticated_user
@allowed_users(allowed_roles={'superuser', 'admin'})
def display_list_admin(request):
    get_and_update_dogs()
    all_available_dogs = get_all_available_dogs()

    if request.method == "POST":
        form_data = dict(request.POST)
        del form_data['csrfmiddlewaretoken']

        form_data = dict([(k, v) for k, v in form_data.items() if v[0] is not ""])

        for dog in DogProfile.objects.filter(appt_only=True):
            if dog.shelterluv_id not in form_data.keys():
                dog.appt_only = False
                dog.save()

        for id in form_data.keys():
            update_dog_from_form_data(id, form_data[id])

        return redirect('calendar')

    context = {
        'all_available_dogs': all_available_dogs,
    }

    return render(request, "wishlist/list_admin.html", context)
