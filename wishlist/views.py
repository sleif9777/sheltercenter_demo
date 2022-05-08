from django.shortcuts import render
import requests, json
from django.contrib.auth.models import Group, User
from dashboard.decorators import *
from .models import *

def display_list(request):
    headers = {
        'X-Api-Key': '2955e22f-1c06-470b-95e3-08666a7397b4',
    }

    has_more = True
    offset = 0
    dogs = []

    while has_more:
        dogs_request = requests.get('https://www.shelterluv.com/api/v1/animals?offset={0}&status_type=publishable'.format(offset), headers=headers).json()

        dogs += dogs_request['animals']

        offset += 100
        has_more = dogs_request['has_more']
    # dogs_request = requests.get('https://www.shelterluv.com/api/v1/animals?offset={0}&limit=10&status_type=publishable'.format(offset), headers=headers).json()

    dogs += dogs_request['animals']

    for dog in dogs:
        try:
            existing_dog = Dog.objects.get(shelterluv_id=dog['ID'])
            print('exist', dog['Name'])
            existing_dog.info = dog
            existing_dog.save()
        except:
            print('new', dog['Name'])
            new_dog = Dog()
            new_dog.shelterluv_id = dog['ID']
            new_dog.info = dog
            new_dog.save()

        print(dog['Name'], '\n')

    context = {'dogs': dogs}

    return render(request, "wishlist/list.html", context)
