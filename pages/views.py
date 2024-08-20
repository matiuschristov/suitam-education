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
from datetime import datetime, timedelta, timezone, time

# function home()
    # Arguments
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/' url
#
def home(request):
    return redirect('/calendar/')

# function test_color_scheme()
    # Arguments
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/test/color-scheme/' url which is for test purposes
#
def test_color_scheme(request):
    return render(request, 'color-scheme.html')

# function user_login()
    # Arguments
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/auth/login/' url which handles all login matters
#
def user_login(request):
    if request.method == 'POST':
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
    if request.COOKIES.get('adAuthCookie'):
        return redirect('/calendar/')
    else:
        return render(request, 'login.html')

# function user_logout()
    # Arguments
        # @require_authentication = user must be logged in to access this path
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/auth/logout/' url which clears the authentication cookie
#
@require_authentication
def user_logout(request, user):
    response = redirect('/auth/login/')
    utils.delete_cookie(response, 'adAuthCookie')
    return response

# function app_overview()
    # Arguments
        # @require_authentication = user must be logged in to access this path
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/overview/' url which renders an overview page
#
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

# function app_calendar()
    # Arguments
        # @require_authentication = user must be logged in to access this path
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/calendar/' url which renders a 5-day calendar page
#
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
            timetable_data = intranet.user_timetable(request, timetable_date - timedelta(hours=10))
            print('day {}'.format(timetable_date.strftime('%-d')))
            timetable_week.append({"classes": timetable_data, "day_name": timetable_date.strftime('%a'), "date_num": timetable_date.strftime('%-d'), "date_current": i == 1})
        return timetable_week
    calendar_timetable_cache = calendar_timetable()
    # calendar_timetable_cache = getCache(user_guid, 'calendar_timetable', 5, calendar_timetable)
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

# function api_update_class_color()
    # Arguments
        # @require_authentication = user must be logged in to access this path
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/api/class/color/' url which updates the class color in database
#
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

# function user_profile()
    # Arguments
        # @require_authentication = user must be logged in to access this path
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/profile/' url which renders the user profile page
#
@require_authentication
def user_profile(request, user):
    return render(request, 'user.html', {
        'user': user
    })

# function class_resources()
    # Arguments
        # @require_authentication = user must be logged in to access this path
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/api/class/resources/' url which reponds with json class resources
#
@require_authentication
def class_resources(request, user):
    data = intranet.class_resources(request)
    user_classes = list()
    for user_class in data.get('Types')[0].get('TimetabledClasses'):
        user_classes.append(user_class.get('SubjectDescription'))
    return HttpResponse(json.dumps(data), content_type='text/plain')

# function api_user_information()
    # Arguments
        # @require_authentication = user must be logged in to access this path
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/api/user/information/' url which reponds with json user information
#
@require_authentication
def api_user_information(request, user):
    return HttpResponse(json.dumps(intranet.user_information(request)), content_type='application/json')

# function api_user_photo()
    # Arguments
        # @require_authentication = user must be logged in to access this path
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/api/user/photo/' url which reponds with binary user profile image
#
@require_authentication
def api_user_photo(request, user):
    return HttpResponse(intranet.user_photo(request, user.get('guid')), content_type='image/jpg')

# function api_dashboard_data()
    # Arguments
        # @require_authentication = user must be logged in to access this path
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/api/dashboard/data/' url which reponds with json dashboard data
#
@require_authentication
def api_dashboard_data(request, user):
    data_user_dashboard = intranet.user_dashboard_data(request, guidString=user.get('guid'))
    return HttpResponse(json.dumps(data_user_dashboard), content_type='application/json')

# function api_user_parents()
    # Arguments
        # @require_authentication = user must be logged in to access this path
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # the view with corresponds with the '/api/user/parents/' url which reponds with json user parents
#
@require_authentication
def api_user_parents(request, user):
    data_user_dashboard = intranet.user_dashboard_data(request, guidString=user.get('guid'))
    return HttpResponse(json.dumps(data_user_dashboard.get('ParentLoginAccountData', {}).get('ParentLogins')), content_type='application/json')