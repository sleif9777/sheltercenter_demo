import numpy
import operator
import os
import requests

from datetime import datetime, timedelta
from django.contrib.auth.models import Group, User
from django.db.models import Count
from django.shortcuts import render

from .models import *
from adopter.models import *
from dashboard.decorators import *
from email_mgr.dictionary import *
from email_mgr.email_sender import *
from email_mgr.models import *

api_root = "https://www.shelterluv.com/api/v1/"

def get_past_three_days():
    today = datetime.datetime.today()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    return today, yesterday, two_days_ago

# TO DO
# cleanup formatting
# break into more functions

def get_groups(user):
    try:
        user_groups = set(group.name for group in user.groups.all().iterator())
    except:
        user_groups = set()

    return user_groups


def get_all_available_dogs_from_shelterluv():
    global api_root
    dogs = []
    has_more = True
    headers = {'X-Api-Key': os.environ.get('SHELTERLUV_API_KEY')}
    offset = 0
    
    while has_more:
        request_address = "{0}animals?offset={1}&status_type=publishable".format(
            api_root, offset)
        dogs_request = requests.get(request_address, headers=headers).json()
        dogs += dogs_request['animals']
        offset += 100
        has_more = dogs_request['has_more']

    return dogs


@authenticated_user
@allowed_users(allowed_roles={'adopter'})
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
        dog, created, litter = update_available_dog_from_json(dog_json)

        if not created:
            current_available_dogs.add(dog)
        elif len(litter) > 0:
            litter_obj = LitterObject.objects.get_or_create(
                litter_id=litter)[0]

            if dog not in litter_obj.dogs.iterator():
                litter_obj.dogs.add(dog)

    adopted_dogs = original_available_dogs - current_available_dogs
    
    for dog in adopted_dogs:
        update_adopted_dog(dog)


def update_available_dog_from_json(dog_json):
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
    
    return dog, created, litter


def update_adopted_dog(dog):
    dog_info = get_dog_info(dog.shelterluv_id)

    DogObject.objects.update_or_create(
        pk=dog.id,
        defaults={
            "alter_date": datetime.date(2000,1,1),
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
                "alter_date": datetime.date(2000,1,1),
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
            litter_obj = LitterObject.objects.get_or_create(
                litter_id=litter)[0]

            if dog_obj not in litter_obj.dogs.iterator():
                litter_obj.dogs.add(dog)


def update_all_litters():
    litters = LitterObject.objects.all()

    for litter in litters:
        litter.check_availability()


def get_litters():
    today, yesterday, two_days_ago = get_past_three_days()
    available_litters = LitterObject.objects.annotate(
            num_dogs=Count('dogs')
        ).filter(
            any_available=True, num_dogs__gt=1
        )
    recently_adopted_litters = LitterObject.objects.annotate(
            num_dogs=Count('dogs')
        ).filter(
            any_available=False, 
            latest_update__in=[today, yesterday, two_days_ago],
            num_dogs__gt=1, 
        )

    return available_litters, recently_adopted_litters


@authenticated_user
@allowed_users(allowed_roles={'superuser', 'admin'})
def create_watchlist_email_batch(
        request, message_type, litter_id=None, dog_id=None):
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
    text = strip_tags(html)

    message.html = html
    message.text = text
    message.save()


def update_litter_name(litter_id, litter_name):
    litter_id = litter_id[:-5] #chop off the -name
    litter = LitterObject.objects.get(pk=litter_id)
    litter.name = litter_name
    litter.save()


def update_litter_return(litter_id, return_date):
    litter_id = litter_id[:-7] #chop off the -return
    litter = LitterObject.objects.get(pk=litter_id)
    year, month, day = get_date_from_form_data(return_date)
    litter.return_date = datetime.date(year, month, day)

    for dog in litter.dogs.iterator():
        dog.offsite = True
        dog.foster_date = datetime.date(year, month, day)
        dog.save()

    litter.save()    


def get_litter_and_data_type(key):
    if "-name" in key:
        return "name"
    elif "-return" in key:
        return "return"


@authenticated_user
@allowed_users(allowed_roles={'superuser', 'admin', 'foster_admin'})
def litter_mgmt(request):
    get_and_update_dogs()
    available_litters, recently_adopted_litters = get_litters()

    if request.method == "POST":
        form_data = dict(request.POST)
        del form_data['csrfmiddlewaretoken']

        for key in form_data:
            litter_data = form_data[key][0]
            litter_data_type = get_litter_and_data_type(key)

            if len(litter_data) > 0:
                match litter_data_type:
                    case "name":
                        update_litter_name(key, litter_data)
                    case "return":
                        update_litter_return(key, litter_data)
    
    context = {
        "available_litters": available_litters,
        "recently_adopted_litters": recently_adopted_litters,
    }
    
    return render(request, "wishlist/litters.html", context)


def filter_dogs_adopted_today():
    global api_root
    today, yesterday, two_days_ago = get_past_three_days()
    all_dogs = DogObject.objects.filter(
        update_dt__date__in=[today, yesterday, two_days_ago])
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
    
    request_address = '{0}animals/{1}'.format(api_root, shelterluv_id)
    dogs_request = requests.get(request_address, headers=headers).json()

    return dogs_request


def get_and_update_dogs():
    update_from_shelterluv()
    update_all_litters()
    remove_expired_dates()


def get_all_available_dogs(filter_today=False):
    today, yesterday, two_days_ago = get_past_three_days()

    if filter_today:
        all_available_dogs_query = DogObject.objects.filter(
            shelterluv_status='Available for Adoption'
        ).exclude(
            update_dt__date__in=[today, yesterday, two_days_ago]
        )
    else:
        all_available_dogs_query = DogObject.objects.filter(
            shelterluv_status='Available for Adoption')

    all_available_dogs = [dog for dog in all_available_dogs_query]
    all_available_dogs = sorted(
        all_available_dogs, key=operator.attrgetter('name'))

    return all_available_dogs


def remove_expired_dates():
    today = datetime.datetime.today()
    default_date = datetime.date(2000, 1, 1)
    shifted_date = datetime.date(2000, 1, 2) # exclude true 1/1/2000 default
    
    for dog in DogObject.objects.filter(
            alter_date__range=(shifted_date, today)):
        dog.alter_date = default_date
        dog.offsite = True if dog.appt_only else False
        dog.save()

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
@allowed_users(allowed_roles={'superuser', 'admin', 'foster_admin', 'adopter'})
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
    other_available_dogs = [dog for dog in all_available_dogs 
        if dog not in user_wishlist_arr]
 
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
        if '-altr' in id:
            dog.alter_date = datetime.date(year, month, day)
        elif '-host' in id:
            dog.host_date = datetime.date(year, month, day)
        elif '-fstr' in id:
            dog.foster_date = datetime.date(year, month, day)

    dog.save()


def handle_cleared_dates_in_form(form_data):
    date_default = datetime.date(2000, 1, 1)

    for dog in DogObject.objects.filter(
            appt_only=False,
            alter_date = date_default, 
            foster_date = date_default,
            host_date = date_default,
            offsite=True):
        dog.offsite = False
        dog.save()

    for dog in DogObject.objects.filter(appt_only=True):
        if "{0}-appt".format(dog.shelterluv_id) not in form_data.keys():
            dog.appt_only = False
            dog.offsite = False
            dog.save()

    for dog in DogObject.objects.filter(
            shelterluv_status="Available for Adoption").exclude(
            alter_date=date_default):
        if "{0}-altr".format(dog.shelterluv_id) not in form_data.keys():
            dog.alter_date = date_default
            dog.offsite = True if dog.appt_only else False
            dog.save()
            
    for dog in DogObject.objects.filter(
            shelterluv_status="Available for Adoption").exclude(
            foster_date=date_default):
        if "{0}-fstr".format(dog.shelterluv_id) not in form_data.keys():
            dog.foster_date = date_default
            dog.offsite = True if dog.appt_only else False
            dog.save()

    for dog in DogObject.objects.filter(
            shelterluv_status="Available for Adoption").exclude(
            host_date=date_default):
        if "{0}-host".format(dog.shelterluv_id) not in form_data.keys():
            dog.host_date = date_default
            dog.offsite = True if dog.appt_only else False
            dog.save()


@authenticated_user
@allowed_users(allowed_roles={'superuser', 'admin', 'foster_admin'})
def display_list_admin(request):
    all_available_dogs = get_all_available_dogs(filter_today=True)
    recently_adopted_dogs, recently_posted_dogs = filter_dogs_adopted_today()
    user_groups = get_groups(request.user)
    remove_expired_dates()

    if request.method == "POST":
        form_data = dict(request.POST)
        del form_data['csrfmiddlewaretoken']

        form_data = dict([(k, v) for k, v in form_data.items() if v[0] != ""])
        print(form_data)

        for id in form_data.keys():
            update_dog_from_form_data(id, form_data[id])

        handle_cleared_dates_in_form(form_data)

        if 'admin' in user_groups:
            return redirect('calendar')
        else:
            return redirect('watchlist_status_page')

    context = {
        'all_available_dogs': all_available_dogs,
        'recently_adopted_dogs': recently_adopted_dogs,
        'recently_posted_dogs': recently_posted_dogs,
    }

    return render(request, "wishlist/list_admin.html", context)


def render_status_page(request):
    context = {
        'foster_responsible_dogs': offsite_dogs_by_team("foster"),
        'host_responsible_dogs': offsite_dogs_by_team("host")
    }

    return render(request, "wishlist/watchlist_dashboard.html", context)


def offsite_dogs_by_team(team):
    appt_only = list(DogObject.objects.filter(appt_only=True))
    foster_dogs = list(DogObject.objects.filter(foster_date__gte=today))
    host_dogs = list(DogObject.objects.filter(host_date__gte=today))

    match team:
        case "foster":
            return sorted(list(set(appt_only + foster_dogs)),
                key=lambda x: x.name)
        case "host":
            return host_dogs
    
    return
