import datetime
import operator
import os
import requests

from django.contrib.auth.models import Group, User
from django.db.models import Count
from django.shortcuts import render

from .models import *
from adopter.models import *
from dashboard.decorators import *
from email_mgr.dictionary import *
from email_mgr.email_sender import *
from email_mgr.models import *

today = datetime.datetime.today()
yesterday = datetime.datetime(2023, 1, 5)

# TO DO
# decorators for authentication
# cleanup formatting

def get_groups(user):
    try:
        user_groups = set(group.name for group in user.groups.all().iterator())
    except:
        user_groups = set()

    return user_groups


def get_all_available_dogs_from_shelterluv():
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

    return dogs


def remove_dog_from_wishlist(request, dog_id):
    dog = DogObject.objects.get(pk=dog_id)
    wishlist = request.user.adopter.wishlist
    wishlist.remove(dog)
    return redirect('display_list_adopter')


def get_litter(dog_json):
    return dog_json['LitterGroupId'] if dog_json['LitterGroupId'] else ""


def update_from_shelterluv():
    original_available_dogs = set(get_all_available_dogs())
    current_available_dogs = set()
    dogs = get_all_available_dogs_from_shelterluv()

    for dog_json in dogs:
        litter = get_litter(dog_json)
        dog, created = DogObject.objects.update_or_create(
            shelterluv_id=dog_json['Internal-ID'],
            defaults={
                'name': dog_json['Name'],
                'info': dog_json,
                'litter_group': litter,
                'shelterluv_status': dog_json['Status'],
                'update_dt': datetime.datetime.fromtimestamp(
                    int(dog_json['LastUpdatedUnixTime'])
                )
            }
        )

        if not created:
            current_available_dogs.add(dog)
        elif len(litter) > 0:
            litter_obj = LitterObject.objects.get_or_create(litter_id=litter)[0]

            if dog not in litter_obj.dogs.iterator():
                litter_obj.dogs.add(dog)

    adopted_dogs = original_available_dogs - current_available_dogs
    
    for dog in adopted_dogs:
        dog_info = get_dog_info(dog.shelterluv_id)

        DogObject.objects.update_or_create(
            pk=dog.id,
            defaults={
                "appt_only": False,
                "foster_date": datetime.date(2000,1,1),
                "host_date": datetime.date(2000,1,1),
                "info": dog_info,
                'litter_group': "",
                "offsite": False,
                "shelterluv_status": dog_info['Status'],
                'update_dt': datetime.datetime.fromtimestamp(
                    int(dog_info['LastUpdatedUnixTime'])
                )
            }
        )


def update_all_dogs():
    dogs = DogObject.objects.all()

    for dog in dogs:
        dog_info = get_dog_info(dog.shelterluv_id)
        litter = get_litter(dog_info)
        dog_obj, created = DogObject.objects.update_or_create(
            pk=dog.id,
            defaults={
                "appt_only": False,
                "foster_date": datetime.date(2000,1,1),
                "host_date": datetime.date(2000,1,1),
                "info": dog_info,
                'litter_group': litter,
                "offsite": False,
                "shelterluv_status": dog_info['Status'],
                'update_dt': datetime.datetime.fromtimestamp(
                    int(dog_info['LastUpdatedUnixTime'])
                )
            }
        )

        if len(litter) > 0:
            litter_obj = LitterObject.objects.get_or_create(litter_id=litter)[0]

            if dog_obj not in litter_obj.dogs.iterator():
                litter_obj.dogs.add(dog)


def update_all_litters():
    litters = LitterObject.objects.filter(any_available=True)

    for litter in litters:
        litter.check_availability()


def get_litters():
    available_litters = LitterObject.objects.annotate(
            num_dogs=Count('dogs')
        ).filter(
            any_available=True, num_dogs__gt=1
        )
    recently_adopted_litters = LitterObject.objects.annotate(
            num_dogs=Count('dogs')
        ).filter(
            any_available=False, num_dogs__gt=1, latest_update__in=[today, yesterday]
        )

    return available_litters, recently_adopted_litters


def create_watchlist_email_batch(request, message_type, litter_id=None, dog_id=None):
    if litter_id:
        litter = LitterObject.objects.get(pk=litter_id)
        dog_ids = [dog.id for dog in litter.dogs.iterator()]
        adopter_query = Adopter.objects.filter(wishlist__in=dog_ids)
        
        for adopter in adopter_query:
            create_watchlist_email(adopter, message_type, litter=litter)

        return redirect('litter_mgmt')
    else:
        dog = DogObject.objects.get(pk=dog_id)
        adopter_query = Adopter.objects.filter(wishlist__in=[dog_id])

        for adopter in adopter_query:
            create_watchlist_email(adopter, message_type, dog=dog)

        return redirect('display_list_admin')


def create_watchlist_email(adopter, message_type, litter=None, dog=None):
    message = PendingMessage()
    message.email = adopter.primary_email
    message.subject = "New message from the Saving Grace adoptions team"

    match message_type:
        case "popular":
            template = EmailTemplate.objects.get(
                template_name="Dog Is Popular (Low Chances)")
        case "adopted":
            template = EmailTemplate.objects.get(
                template_name="Dogs Were Adopted")
        case _:
            return

    html = replacer(template.text, adopter, None, litter=litter, dog=dog)
    text = strip_tags(html, adopter, None)

    message.html = html
    message.text = text
    message.save()


def update_litter_name(litter_id, litter_name):
    litter_id = litter_id[:-5] #chop off the -name
    litter = LitterObject.objects.get(pk=litter_id)
    litter.name = litter_name
    litter.save()


def litter_mgmt(request):
    global today, yesterday
    update_all_litters()
    available_litters, recently_adopted_litters = get_litters()

    if request.method == "POST":
        form_data = dict(request.POST)
        del form_data['csrfmiddlewaretoken']

        for litter in form_data:
            litter_name = form_data[litter][0]

            if len(litter_name) > 0:
                update_litter_name(litter, litter_name)
  
    context = {
        "available_litters": available_litters,
        "recently_adopted_litters": recently_adopted_litters,
    }
    
    return render(request, "wishlist/litters.html", context)


def filter_dogs_adopted_today():
    global today, yesterday
    all_dogs = DogObject.objects.filter(update_dt__date__in=[today, yesterday])
    adopted_dogs = []
    posted_dogs = []

    for dog in all_dogs:
        if dog.shelterluv_status == "Available for Adoption":
            posted_dogs += [dog]
        else:
            adopted_dogs += [dog]

    return adopted_dogs, posted_dogs


def get_dog_info(shelterluv_id):
    headers = {'X-Api-Key': os.environ.get('SHELTERLUV_API_KEY')}
    
    request_address = 'https://www.shelterluv.com/api/v1/animals/{0}'.format(shelterluv_id)
    dogs_request = requests.get(request_address, headers=headers).json()

    return dogs_request     


def get_and_update_dogs():
    update_from_shelterluv()
    update_all_litters()
    remove_expired_dates()


def get_all_available_dogs(filter_today=False):
    global today, yesterday
    # update_all_dogs()
    update_all_litters()

    if filter_today:
        all_available_dogs_query = DogObject.objects.filter(
            shelterluv_status='Available for Adoption'
        ).exclude(
            update_dt__date__in=[today, yesterday]
        )
    else:
        all_available_dogs_query = DogObject.objects.filter(
            shelterluv_status='Available for Adoption')

    all_available_dogs = [dog for dog in all_available_dogs_query]
    all_available_dogs = sorted(all_available_dogs, key=operator.attrgetter('name'))

    return all_available_dogs


def remove_expired_dates():
    today = datetime.datetime.today()
    default_date = datetime.date(2000, 1, 1)
    shifted_date = datetime.date(2000, 1, 2) # to exclude true 1/1/2000 default
    
    for dog in DogObject.objects.filter(
            host_date__range=(shifted_date, today)):
        dog.host_date = default_date
        dog.offsite = True if dog.appt_only else False
        dog.save()

    for dog in DogObject.objects.filter(
            foster_date__range=(shifted_date, today)):
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
    get_and_update_dogs()

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

        for id in form_data:
            user_wishlist.add(DogObject.objects.get(shelterluv_id=id))

    all_available_dogs = get_all_available_dogs()
    user_wishlist_arr = [dog for dog in user_wishlist.iterator()]
    other_available_dogs = [dog for dog in all_available_dogs if dog not in user_wishlist_arr]
 
    context = {
        'other_available_dogs': other_available_dogs,
        'user_wishlist': user_wishlist_arr,
    }

    return render(request, "wishlist/list_adopter.html", context)


def update_dog_from_form_data(id, form_data):
    dog = DogObject.objects.get(shelterluv_id=id[:-5])
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
    all_available_dogs = get_all_available_dogs(filter_today=True)
    recently_adopted_dogs, recently_posted_dogs = filter_dogs_adopted_today()

    if request.method == "POST":
        form_data = dict(request.POST)
        del form_data['csrfmiddlewaretoken']

        form_data = dict([(k, v) for k, v in form_data.items() if v[0] != ""])

        for dog in DogObject.objects.filter(appt_only=True):
            if dog.shelterluv_id not in form_data.keys():
                dog.appt_only = False
                dog.save()

        for id in form_data.keys():
            update_dog_from_form_data(id, form_data[id])

        return redirect('calendar')

    context = {
        'all_available_dogs': all_available_dogs,
        'recently_adopted_dogs': recently_adopted_dogs,
        'recently_posted_dogs': recently_posted_dogs,
    }

    return render(request, "wishlist/list_admin.html", context)
