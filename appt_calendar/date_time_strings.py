import datetime
import os
import time

is_windows = os.environ.get('WINDOWS')

def date_str(date):
    if is_windows:
        return date.strftime("%A, %B %#d, %Y")
    else:
        return date.strftime("%A, %B %-d, %Y")

def date_no_weekday_str(date):
    if is_windows:
        return date.strftime("%B %#d, %Y")
    else:
        return date.strftime("%B %-d, %Y")

def weekday_str(date):
    return date.strftime("%A")

def time_str(time):
    if is_windows:
        return time.strftime("%#I:%M%p")
    else:
        return time.strftime("%-I:%M%p")

def date_no_year_str(date):
    if is_windows:
        return date.strftime("%A, %#m/%#d")
    else:
        return date.strftime("%A, %-m/%-d")

def next_bd_open(hour, minute):
    if is_windows:
        return datetime.time(hour, minute).strftime("%#I:%M%p").lower()
    else:
        return datetime.time(hour, minute).strftime("%-I:%M%p").lower()
