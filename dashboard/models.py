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
    ac_show_internal_notes = models.BooleanField(default=True)
    ac_show_adopter_notes = models.BooleanField(default=True)
    ac_show_shelterluv_notes = models.BooleanField(default=True)
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
    ac_show_limited_small_dogs_comm = models.BooleanField(default=True)
    ac_show_limited_small_puppies_comm = models.BooleanField(default=True)
    ac_show_lives_with_parents_comm = models.BooleanField(default=True)
    ac_show_limited_puppies_comm = models.BooleanField(default=True)
    ac_show_limited_hypo_comm = models.BooleanField(default=True)
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
            'internal-notes': int(self.ac_show_internal_notes),
            'adopter-notes': int(self.ac_show_adopter_notes),
            'shelterluv-notes': int(self.ac_show_shelterluv_notes),
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
            'limited-small-dogs-comm': int(self.ac_show_limited_small_dogs_comm),
            'limited-small-puppies-comm': int(self.ac_show_limited_small_puppies_comm),
            'lives-with-parents-comm': int(self.ac_show_lives_with_parents_comm),
            'limited-puppies-comm': int(self.ac_show_limited_puppies_comm),
            'limited-hypo-comm': int(self.ac_show_limited_hypo_comm),
            'send-follow-up': int(self.ac_show_send_follow_up),
            'send-follow-up-with-host': int(self.ac_show_send_follow_up_with_host),
            'schedule-next': int(self.ac_show_schedule_next)
        }

        return attributes

    def get_card_subblock_settings(self):
        notes = [
            self.ac_show_internal_notes,
            self.ac_show_adopter_notes,
            self.ac_show_shelterluv_notes
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
            'notes': int(all(setting for setting in notes)),
            'about': int(all(setting for setting in about)),
            'preferences': int(all(setting for setting in preferences)),
            'follow_ups': int(all(setting for setting in follow_ups))
        }

        return subblocks
