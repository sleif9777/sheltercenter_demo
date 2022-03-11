def clean_name(name):
    # takes an all caps or all lowers name and converts to title case

    return name[0].upper() + name[1:].lower()

def chg_appt_status(adopter):
    # changes has_current_appt for an adopter object

    adopter.has_current_appt = not adopter.has_current_appt
    adopter.save()
# 
# def create_email(fname, lname):
#     # creates a default shelterluv email address
