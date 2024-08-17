from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from scraper import intranet
from pages import utils
from pages.decorators import *
from pages.jsonstore import JSONStore
import json
import random
import urllib
from datetime import datetime, timedelta, timezone

db = JSONStore()


def view_home(request):
    return redirect('/overview/')

def view_test(request):
    return render(request, 'test.html')

def view_test_color_scheme(request):
    return render(request, 'color-scheme.html')

def view_user_login(request):
    if request.POST:
        login_details = urllib.parse.parse_qs(request.body.decode("utf-8"))
        if not login_details.get('username')[0] or not login_details.get('password')[0]:
            return HttpResponse('Login requires username and password')
        auth = intranet.login(login_details.get('username')[0], login_details.get('password')[0])
        auth_redirect = redirect('/calendar/')
        if auth:
            for header in auth:
                utils.set_cookie(auth_redirect, header, auth[header], days_expire=7)
            return auth_redirect
        else:
            print('authentication failed')
            return redirect('/auth/login')
    if request.COOKIES.get('ASP.NET_SessionId') and request.COOKIES.get('adAuthCookie'):
        return HttpResponse('You are already logged in.')
    else:
        return render(request, 'login.html')

@require_authentication
def view_user_logout(request):
    response = redirect('/auth/login/')
    utils.delete_cookie(response, 'ASP.NET_SessionId')
    utils.delete_cookie(response, 'adAuthCookie')
    return response

def getCache(user: str, name: str, expires: int, data):
    cache = {}
    if db.exists('user-cache', user):
        cache = db.get('user-cache', user);
    cache_data = cache.get(name)
    if not cache_data or cache_data.get('expires') < int(datetime.now().timestamp()):
        cache_data = data()
        cache[name] = { "expires": int((datetime.now() + timedelta(minutes=expires)).timestamp()), "data": cache_data}
        db.save('user-cache', user, cache)
        cache = cache_data
    else:
        print('got {} from cache\nuser: {}'.format(name, user))
        cache = cache.get(name, {}).get('data')
    return cache

def apply_event_colors(guid, classes):
    settings = dict()
    if db.exists('user', guid):
        settings = db.get('user', guid)
    for period in classes:
        period['color'] = settings.get('classes') and settings.get('classes').get(str(period.get('id'))) and settings.get('classes').get(str(period.get('id'))).get('color')
        if not period.get('color'):
            period['color'] = 'gray'
        period['data'] = json.dumps(period)
    return classes

@require_authentication
def view_overview(request):
    user_information = intranet.user_information(request)
    user_information['initals'] = "".join(list(map(lambda x: x[0], user_information.get('name').split(' '))))
    user_guid = user_information.get('guid')

    
    def overview_timetable():
        return intranet.user_timetable(request, datetime.today() + timedelta(days=3))
    overview_timetable_cache = getCache(user_guid, 'overview_timetable', 2, overview_timetable)
    overview_timetable_cache = apply_event_colors(user_guid, overview_timetable_cache)

    return render(request, 'overview.html', {
        'user': user_information,
        'timetable': overview_timetable_cache
    })

@require_authentication
def view_calendar(request):
    user_information = intranet.user_information(request)
    user_information['initals'] = "".join(list(map(lambda x: x[0], user_information.get('name').split(' '))))
    user_guid = user_information.get('guid')

    def calendar_timetable():
        timetable_week = []
        i = 0;
        while len(timetable_week) < 6:
            timetable_date = datetime.today() + timedelta(days=i)
            i += 1
            if timetable_date.weekday() >= 5:
                continue;
            timetable_data = intranet.user_timetable(request, timetable_date)
            timetable_week.append({"classes": timetable_data, "day_name": timetable_date.strftime('%a'), "date_num": timetable_date.strftime('%-d'), "date_current": i == 1})
        return timetable_week
    calendar_timetable_cache = getCache(user_guid, 'calendar_timetable', 5, calendar_timetable)
    for day in calendar_timetable_cache:
        day['classes'] = apply_event_colors(user_guid, day.get('classes'))
    
    def calendar_classes():
        user_class_resources = intranet.class_resources(request)
        user_classes = list()
        for user_class in user_class_resources.get('Types')[0].get('TimetabledClasses'):
            class_name = user_class.get('SubjectDescription').lower()
            if class_name.endswith('assembly'):
                continue;
            elif class_name.endswith('pastoral care'):
                continue;
            user_classes.append({
                'class_id': user_class.get('ClassID'),
                'class_code': user_class.get('ClassCode'),
                'class_name': utils.class_correct_capitalisation(class_name),
                'subject_id': user_class.get('SubjectID'),
                'subject_code': user_class.get('SubjectCode'),
                'task_count_assessment': user_class.get('AssessmentTaskCount'),
                'task_count_derived': user_class.get('DerivedTaskCount'),
                'task_count_classwork': user_class.get('ClassworkTaskCount'),
                'task_count_overdue': user_class.get('OverdueTaskCount'),
                'teachers': user_class.get('Teachers')
            })
        return user_classes
    calendar_classes_cache = getCache(user_guid, 'calendar_classes', 5,  calendar_classes)

    return render(request, 'calendar.html', {
        'user': user_information,
        'timetable': calendar_timetable_cache,
        'classes': calendar_classes_cache
    })

@require_authentication
def api_update_class_color(request):
    user_information = intranet.user_information(request)
    user_guid = user_information.get('guid')
    if not request.method == "POST":
        return HttpResponse(status=405)
    try:
        request_data = json.loads(request.body.decode('utf-8'))
        class_id = request_data.get('id')
        if not class_id:
            return HttpResponse(status=400)
        settings = dict()
        if db.exists('user', user_guid):
            settings = db.get('user', user_guid)
        classes = settings.get('classes')
        if not classes:
            classes = dict()
        if not classes.get(class_id):
            classes[class_id] = dict()
        classes[class_id]['color'] = request_data['color']
        settings['classes'] = classes
        print(settings)
        db.save('user', user_guid, settings)
    except:
        print('An exception occurred')
    return HttpResponse(status=200)

@require_authentication
def view_user_profile(request):
    return render(request, 'user.html', {
        'user': intranet.user_information(request)
    })

@require_authentication
def view_class_resources(request):
    data = intranet.class_resources(request)
    user_classes = list()
    for user_class in data.get('Types')[0].get('TimetabledClasses'):
        user_classes.append(user_class.get('SubjectDescription'))
    return HttpResponse(json.dumps(data), content_type='text/plain')

@require_authentication
def api_user_information(request):
    return HttpResponse(json.dumps(intranet.user_information(request)), content_type='application/json')

@require_authentication
def api_user_photo(request):
    return HttpResponse(intranet.user_photo(request), content_type='image/jpg')

@require_authentication
def api_dashboard_data(request):
    data_user_information = intranet.user_information(request)
    data_user_dashboard = intranet.user_dashboard_data(request, guidString=data_user_information.get('guid'))
    return HttpResponse(json.dumps(data_user_dashboard), content_type='application/json')

@require_authentication
def api_user_parents(request):
    data_user_information = intranet.user_information(request)
    data_user_dashboard = intranet.user_dashboard_data(request, guidString=data_user_information.get('guid'))
    return HttpResponse(json.dumps(data_user_dashboard.get('ParentLoginAccountData', {}).get('ParentLogins')), content_type='application/json')