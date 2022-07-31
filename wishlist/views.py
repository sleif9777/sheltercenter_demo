import json
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

    # for dog in all_dogs_in_db:
    #     dog_req = requests.get('https://www.shelterluv.com/api/v1/animals/{0}'.format(dog.shelterluv_id), headers=headers).json()
    #
    #     if dog.shelterluv_status != dog_req['Status']:
    #         dog.shelterluv_status = dog_req['Status']
    #         dog.save()

    # get all currently available_dogs
    while has_more:
        dogs_request = requests.get('https://www.shelterluv.com/api/v1/animals?offset={0}&status_type=publishable'.format(offset), headers=headers).json()

        dogs += dogs_request['animals']

        offset += 100
        has_more = dogs_request['has_more']

    # try to call dog, if not existing, create object and save
    for dog in dogs:
        dog = Dog.objects.update_or_create(shelterluv_id=dog['Internal-ID'], info=dog, shelterluv_status=dog['Status'], name=dog['Name'])
        #
        # try:
        #     # find a dog that may exist already (surrender or return from foster)
        #     existing_dog = Dog.objects.get(shelterluv_id=dog['Internal-ID'])
        #     existing_dog.info = dog
        #     existing_dog.shelterluv_status = dog['Status']
        #     existing_dog.save()
        # except Exception as e:
        #     # if net new, create object
        #     print('e2', e)
        #     new_dog = Dog()
        #     new_dog.name = dog['Name']
        #     new_dog.shelterluv_id = dog['Internal-ID']
        #     new_dog.shelterluv_status = dog['Status']
        #     new_dog.info = dog
        #     new_dog.save()

    # with updated list, call all dogs listed as available in database
    current_available_dogs = [dog for dog in Dog.objects.filter(shelterluv_status="Available for Adoption")]

    # determine which dogs were recently removed from website
    recent_delisted = [dog for dog in previous_available_dogs if dog not in current_available_dogs]

    for dog in recent_delisted:
        dog_req = requests.get('https://www.shelterluv.com/api/v1/animals/{0}'.format(dog.shelterluv_id), headers=headers).json()
        dog.shelterluv_status = dog_req['Status']
        dog.save()

def check_for_updated_status():
    available_dogs = Dog.objects.get(shelterluv_status="Available for Adoption")

    for dog in available_dogs:
        update_request = requests.get('https://www.shelterluv.com/api/v1/animals?offset={0}&status_type=publishable'.format(offset), params=params, headers=headers).json()

@authenticated_user
@allowed_users(allowed_roles={'superuser'})
def display_list(request):
    # get_and_update_dogs()

    # user_wishlist = {dog for dog in request.user.adopter.wishlist.iterator()}
    all_available_dogs = [dog for dog in Dog.objects.filter(shelterluv_status = 'Available for Adoption').order_by('name')]

    print([dog.name for dog in all_available_dogs])

    # other_available_dogs = all_available_dogs - user_wishlist

    if request.method == "POST":
        form_data = dict(request.POST)
        del form_data['csrfmiddlewaretoken']
        print(type(form_data.keys()))

        for dog in Dog.objects.filter(offsite=True):
            if dog.shelterluv_id not in form_data.keys():
                dog.offsite = False
                dog.save()

        for id in form_data.keys():
            dog = Dog.objects.get(shelterluv_id=id)
            dog.offsite = True
            dog.save()

        return redirect('calendar')

        # for id in form_data:
        #     print(id)
        #     user_wishlist.add(Dog.objects.get(shelterluv_id=id))
        #
        # print(request.user.adopter.wishlist)
        # for dog in all_available_dogs:
        #     add_to_wishlist = request.form[dog.shelterluv_id]

    context = {
        'all_available_dogs': all_available_dogs,
        # 'form': form
        # 'user_wishlist': user_wishlist,
    }

    return render(request, "wishlist/list.html", context)
