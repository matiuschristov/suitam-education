from django.conf import settings
from pages.jsonstore import db
import datetime
import json

def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )
    response.set_cookie(
        key,
        value,
        max_age=max_age,
        expires=expires,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE or None,
    )

def delete_cookie(response, key):
    response.delete_cookie(
        key,
        domain=settings.SESSION_COOKIE_DOMAIN,
    )

def class_correct_capitalisation(subject):
    subject = subject.lower().split(' ')
    del subject[0:2]
    updated = list()
    keepLowerCase = ['and', 'at']
    for x in subject:
        if x == 'pe':
            x = x.upper()
        elif x == 'it' or x == 'it:':
            # x = x.upper()
            continue;
        elif not [match for match in keepLowerCase if x in match]:
            x = x.title()
        updated.append(x)
    return " ".join(updated)

def event_colors(guid, classes):
    settings = dict()
    if db.exists('user', guid):
        settings = db.get('user', guid)
    for period in classes:
        period['color'] = settings.get('classes') and settings.get('classes').get(str(period.get('id'))) and settings.get('classes').get(str(period.get('id'))).get('color')
        if not period.get('color'):
            period['color'] = 'gray'
        period['data'] = json.dumps(period)
    return classes