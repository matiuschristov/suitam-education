from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from scraper import intranet
from pages import utils
from pages.cache import *
from pages.decorators import *
from pages.exception import *
from pages.jsonstore import db
import json
import urllib
from datetime import datetime, timedelta

def home(request):
    return redirect('/calendar/')

def test_color_scheme(request):
    return render(request, 'color-scheme.html')

def user_login(request):
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
            return redirect('/auth/login?code=USERNAME-PASSSWORD-INCORRECT')
    if request.COOKIES.get('ASP.NET_SessionId') and request.COOKIES.get('adAuthCookie'):
        return HttpResponse('You are already logged in.')
    else:
        return render(request, 'login.html')

@require_authentication
def user_logout(request, user):
    response = redirect('/auth/login/')
    utils.delete_cookie(response, 'adAuthCookie')
    return response

@require_authentication
def app_overview(request, user):
    user['initals'] = "".join(list(map(lambda x: x[0], user.get('name').split(' '))))
    user_guid = user.get('guid')
    
    def overview_timetable():
        return intranet.user_timetable(request)
    overview_timetable_cache = getCache(user_guid, 'overview_timetable', 2, overview_timetable)
    overview_timetable_cache = utils.event_colors(user_guid, overview_timetable_cache)

    return render(request, 'overview.html', {
        'user': user,
        'timetable': overview_timetable_cache
    })

@require_authentication
def app_calendar(request, user):
    user['initals'] = "".join(list(map(lambda x: x[0], user.get('name').split(' '))))
    user_guid = user.get('guid')

    def calendar_timetable():
        timetable_week = []
        i = 0;
        while len(timetable_week) < 6:
            timetable_date = datetime.utcnow() + timedelta(days=i,hours=10)
            i += 1
            if timetable_date.weekday() >= 5:
                continue;
            timetable_data = intranet.user_timetable(request, timetable_date)
            timetable_week.append({"classes": timetable_data, "day_name": timetable_date.strftime('%a'), "date_num": timetable_date.strftime('%-d'), "date_current": i == 1})
        return timetable_week
    calendar_timetable_cache = getCache(user_guid, 'calendar_timetable', 5, calendar_timetable)
    for day in calendar_timetable_cache:
        day['classes'] = utils.event_colors(user_guid, day.get('classes'))
    
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
        'user': user,
        'timetable': calendar_timetable_cache,
        'classes': calendar_classes_cache
    })

@require_authentication
def api_update_class_color(request, user):
    user_guid = user.get('guid')
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
        db.save('user', user_guid, settings)
    except:
        print('An exception occurred')
    return HttpResponse(status=200)

@require_authentication
def user_profile(request, user):
    return render(request, 'user.html', {
        'user': user
    })

@require_authentication
def class_resources(request, user):
    data = intranet.class_resources(request)
    user_classes = list()
    for user_class in data.get('Types')[0].get('TimetabledClasses'):
        user_classes.append(user_class.get('SubjectDescription'))
    return HttpResponse(json.dumps(data), content_type='text/plain')

@require_authentication
def api_user_information(request, user):
    return HttpResponse(json.dumps(intranet.user_information(request)), content_type='application/json')

@require_authentication
def api_user_photo(request, user):
    return HttpResponse(intranet.user_photo(request, user.get('guid')), content_type='image/jpg')

@require_authentication
def api_dashboard_data(request, user):
    data_user_dashboard = intranet.user_dashboard_data(request, guidString=user.get('guid'))
    return HttpResponse(json.dumps(data_user_dashboard), content_type='application/json')

@require_authentication
def api_user_parents(request, user):
    data_user_dashboard = intranet.user_dashboard_data(request, guidString=user.get('guid'))
    return HttpResponse(json.dumps(data_user_dashboard.get('ParentLoginAccountData', {}).get('ParentLogins')), content_type='application/json')