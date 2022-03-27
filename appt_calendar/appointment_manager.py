from adopter.adopter_manager import *

def reset_appt(appt):
    # clears all information out of an appointment and republishes it for booking

    appt.adopter_choice = None
    appt.available = True
    appt.published = True
    appt.outcome = "1"
    appt.internal_notes = ""
    appt.adopter_notes = ""
    appt.bringing_dog = False
    appt.has_cat = False
    appt.mobility = False
    appt.comm_adopted_dogs = False
    appt.comm_limited_puppies = False
    appt.comm_limited_small = False
    appt.comm_limited_hypo = False
    appt.comm_limited_other = False
    appt.save()

def delist_appt(appt):
    # sets the adopter upon booking and changes their appt status, turns off the publish and available attributes of an appt

    appt.available = False
    appt.published = False
    appt.save()
