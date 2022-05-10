from django.shortcuts import render
import requests, json, os
from django.contrib.auth.models import Group, User
from dashboard.decorators import *
from .models import *

def get_and_update_dogs():
    headers = {
        'X-Api-Key': os.environ.get('SHELTERLUV_API_KEY'),
    }

    has_more = True
    offset = 0
    dogs = []

    while has_more:
        dogs_request = requests.get('https://www.shelterluv.com/api/v1/animals?offset={0}&status_type=publishable'.format(offset), headers=headers).json()

        dogs += dogs_request['animals']

        offset += 100
        has_more = dogs_request['has_more']

    for dog in dogs:
        try:
            existing_dog = Dog.objects.get(shelterluv_id=dog['ID'])
            existing_dog.info = dog
            existing_dog.shelterluv_status = dog['Status']
            existing_dog.save()
        except:
            new_dog = Dog()
            new_dog.shelterluv_id = dog['ID']
            new_dog.shelterluv_status = dog['Status']
            new_dog.info = dog
            new_dog.save()


def display_list(request):
    # get_and_update_dogs()

    user_wishlist = {dog for dog in request.user.adopter.wishlist.iterator()}
    all_available_dogs = {dog for dog in Dog.objects.filter(shelterluv_status = 'Available for Adoption').order_by('shelterluv_id')}

    other_available_dogs = all_available_dogs - user_wishlist

    if request.method == "POST":
        form_data = dict(request.POST)
        del form_data['csrfmiddlewaretoken']

        for id in form_data:
            print(id)
            user_wishlist.add(Dog.objects.get(shelterluv_id=id))

        print(request.user.adopter.wishlist)
        # for dog in all_available_dogs:
        #     add_to_wishlist = request.form[dog.shelterluv_id]

    context = {
        'all_available_dogs': all_available_dogs,
        'user_wishlist': user_wishlist,
    }

    return render(request, "wishlist/list.html", context)
