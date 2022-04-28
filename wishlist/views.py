from django.shortcuts import render
import requests
from django.contrib.auth.models import Group, User
from dashboard.decorators import *

@authenticated_user
@allowed_users(allowed_roles={'superuser'})
def list_of_dogs(request):
    headers = {'x-api-key': '2955e22f-1c06-470b-95e3-08666a7397b4'}

    response = requests.get('https://www.shelterluv.com/api/v1/animals?=', headers=headers).json()
    x = 100

    dogs = [dog for dog in response['animals'] if dog['Status'] == "Available for Adoption" and dog['Description'] != ""]

    while response['animals'] != [] and x <= 3000:
        response = requests.get('https://www.shelterluv.com/api/v1/animals?=&offset={0}'.format(x), headers=headers).json()

        for dog in [dog for dog in response['animals'] if dog['Status'] == "Available for Adoption" and dog['Description'] != ""]:
            dogs.append(dog)

        x += 100

    print(len(dogs))

    return render(request, 'wishlist/list.html', {'dogs': dogs})
