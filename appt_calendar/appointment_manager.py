from copy import copy

from adopter.adopter_manager import *

def reset_appt(appt):
    # clears all information out of an appointment and republishes it for booking

    appt.adopter = None
    appt.available = True
    appt.published = True
    appt.outcome = "1"
    appt.internal_notes = ""
    appt.adopter_notes = ""
    appt.dog = ""
    appt.dog_fka = ""
    appt.bringing_dog = False
    appt.has_cat = False
    appt.mobility = False
    appt.comm_adopted_dogs = False
    appt.comm_limited_puppies = False
    appt.comm_limited_small = False
    appt.comm_limited_hypo = False
    appt.comm_limited_other = False
    appt.comm_limited_small_puppies = False
    appt.visits_to_date = 0
    appt.last_update_sent = None
    appt.paperwork_complete = False
    appt.save()

def delist_appt(appt):
    # sets the adopter upon booking and changes their appt status, turns off the publish and available attributes of an appt

    appt.available = False
    appt.published = False

    if appt.adopter != None:
        appt.visits_to_date = copy(appt.adopter.visits_to_date)

    if appt.adopter.acknowledged_faq == False:
        appt.adopter.acknowledged_faq = True
        appt.adopter.save()

    appt.save()
