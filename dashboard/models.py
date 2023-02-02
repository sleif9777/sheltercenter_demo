from email.policy import default
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    first_name = models.CharField(default="", max_length=200)
    last_name = models.CharField(default="", max_length=200)
    signature = models.TextField(default="")
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

    #appointment card attributes
    ac_show_number_of_visits = models.BooleanField(default=True)
    ac_show_adopter_email = models.BooleanField(default=True)
    ac_show_adopter_phone = models.BooleanField(default=True)
    ac_show_adopter_description = models.BooleanField(default=True)
    ac_show_counselor = models.BooleanField(default=True)
    ac_show_internal_notes = models.BooleanField(default=True)
    ac_show_adopter_notes = models.BooleanField(default=True)
    ac_show_shelterluv_notes = models.BooleanField(default=True)
    ac_show_watchlist = models.BooleanField(default=True)
    ac_show_city_state = models.BooleanField(default=True)
    ac_show_household_activity = models.BooleanField(default=True)
    ac_show_housing = models.BooleanField(default=True)
    ac_show_fence = models.BooleanField(default=True)
    ac_show_booking_timestamp = models.BooleanField(default=True)
    ac_show_gender_preference = models.BooleanField(default=True)
    ac_show_weight_preference = models.BooleanField(default=True)
    ac_show_age_preference = models.BooleanField(default=True)
    ac_show_hypo_preference = models.BooleanField(default=True)
    ac_show_breed_restriction_comm = models.BooleanField(default=True)
    ac_show_dogs_adopted_comm = models.BooleanField(default=True)
    ac_show_dog_in_extended_host_comm = models.BooleanField(default=True)
    ac_show_dog_in_medical_foster_comm = models.BooleanField(default=True)
    ac_show_dog_is_popular_low_chances_comm = models.BooleanField(default=True)
    ac_show_dog_is_popular_comm = models.BooleanField(default=True)
    ac_show_dog_not_here_yet_comm = models.BooleanField(default=True)
    ac_show_limited_hypo_comm = models.BooleanField(default=True)
    ac_show_limited_puppies_comm = models.BooleanField(default=True)
    ac_show_limited_small_dogs_comm = models.BooleanField(default=True)
    ac_show_limited_small_puppies_comm = models.BooleanField(default=True)
    ac_show_lives_with_parents_comm = models.BooleanField(default=True)
    ac_show_send_follow_up = models.BooleanField(default=True)
    ac_show_send_follow_up_with_host = models.BooleanField(default=True)
    ac_show_schedule_next = models.BooleanField(default=True)

    def __repr__(self):
        return self.user.username

    def __str__(self):
        return self.user.username

    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def get_card_settings(self):
        attributes = {
            'number-of-visits': int(self.ac_show_number_of_visits),
            'adopter-email': int(self.ac_show_adopter_email),
            'adopter-phone': int(self.ac_show_adopter_phone),
            'adopter-description': int(self.ac_show_adopter_description),
            'counselor': int(self.ac_show_counselor),
            'internal-notes': int(self.ac_show_internal_notes),
            'adopter-notes': int(self.ac_show_adopter_notes),
            'shelterluv-notes': int(self.ac_show_shelterluv_notes),
            'ac_show_watchlist': int(self.ac_show_watchlist),
            'city-state': int(self.ac_show_city_state),
            'household-activity': int(self.ac_show_household_activity),
            'housing': int(self.ac_show_housing),
            'fence': int(self.ac_show_fence),
            'booking-timestamp': int(self.ac_show_booking_timestamp),
            'gender-preference': int(self.ac_show_gender_preference),
            'weight-preference': int(self.ac_show_weight_preference),
            'age-preference': int(self.ac_show_age_preference),
            'hypo-preference': int(self.ac_show_hypo_preference),
            'breed-restriction-comm': int(self.ac_show_breed_restriction_comm),
            'dogs-adopted-comm': int(self.ac_show_dogs_adopted_comm),
            'dog-in-extended-host-comm': int(self.ac_show_dog_in_extended_host_comm),
            'dog-in-medical-foster-comm': int(self.ac_show_dog_in_medical_foster_comm),
            'dog-is-popular-comm': int(self.ac_show_dog_is_popular_comm),
            'dog-is-popular-low-chances-comm': int(self.ac_show_dog_is_popular_low_chances_comm),
            'dog-not-here-yet-comm': int(self.ac_show_dog_not_here_yet_comm),
            'limited-hypo-comm': int(self.ac_show_limited_hypo_comm),
            'limited-puppies-comm': int(self.ac_show_limited_puppies_comm),
            'limited-small-dogs-comm': int(self.ac_show_limited_small_dogs_comm),
            'limited-small-puppies-comm': int(self.ac_show_limited_small_puppies_comm),
            'lives-with-parents-comm': int(self.ac_show_lives_with_parents_comm),
            'send-follow-up': int(self.ac_show_send_follow_up),
            'send-follow-up-with-host': int(self.ac_show_send_follow_up_with_host),
            'schedule-next': int(self.ac_show_schedule_next)
        }

        return attributes

    def get_card_subblock_settings(self):
        contact = [
            self.ac_show_adopter_email,
            self.ac_show_adopter_phone,
            self.ac_show_adopter_description,
            self.ac_show_counselor
        ]

        notes = [
            self.ac_show_internal_notes,
            self.ac_show_adopter_notes,
            self.ac_show_shelterluv_notes,
            self.ac_show_watchlist,
        ]
        
        about = [
            self.ac_show_city_state,
            self.ac_show_household_activity,
            self.ac_show_housing,
            self.ac_show_fence,
            self.ac_show_booking_timestamp
        ]

        preferences = [
            self.ac_show_gender_preference,
            self.ac_show_weight_preference,
            self.ac_show_age_preference,
            self.ac_show_hypo_preference
        ]

        follow_ups = [
            self.ac_show_send_follow_up,
            self.ac_show_send_follow_up_with_host,
            self.ac_show_schedule_next
        ]

        subblocks = {
            'contact': int(any(setting for setting in contact)),
            'notes': int(any(setting for setting in notes)),
            'about': int(any(setting for setting in about)),
            'preferences': int(any(setting for setting in preferences)),
            'follow_ups': int(any(setting for setting in follow_ups))
        }

        return subblocks
