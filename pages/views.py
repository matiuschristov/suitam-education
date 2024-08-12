from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from scraper import intranet
from pages import utils
from pages.decorators import *
import json
import random
import urllib
from datetime import datetime, timedelta

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

@require_authentication
def view_overview(request):
    user_information = intranet.user_information(request)
    user_information['initals'] = "".join(list(map(lambda x: x[0], user_information.get('name').split(' '))))
    
    # user_class_resources = intranet.class_resources(request)
    # user_classes = list()
    # for user_class in user_class_resources.get('Types')[0].get('TimetabledClasses'):
    #     class_name = user_class.get('SubjectDescription').lower()
    #     if class_name.endswith('assembly'):
    #         continue;
    #     elif class_name.endswith('pastoral care'):
    #         continue;
    #     user_classes.append(class_name)

    # user_periods = intranet.user_timetable(request).get('Periods')

    # for x, period in enumerate(user_periods):
    #     print(period)
    #     user_periods[x]['position'] = int(x) * 109;
        # should be 110 made 114 for temporary spacing

    return render(request, 'overview.html', {
        'user': user_information
        # 'classes': list(map(correct_capitalisation, user_classes)),
        # 'timetable': user_periods
    })

@require_authentication
def view_calendar(request):
    user_information = intranet.user_information(request)
    user_information['initals'] = "".join(list(map(lambda x: x[0], user_information.get('name').split(' '))))

    timetable_week = []
    for i in range(7):
        timetable_date = datetime.today() + timedelta(days=i)
        timetable_data = intranet.user_timetable(request, timetable_date)
        timetable = []
        for period in timetable_data.get('Periods'):
            classes = period.get('Classes')
            if len(classes) == 0:
                continue;
            timetable.append({
                'code': classes[0].get('TimeTableClass'),
                'name': utils.class_correct_capitalisation(classes[0].get('Description')),
                'teacher': classes[0].get('TeacherName'),
                'room': classes[0].get('Room'),
                'id': classes[0].get('ClassID'),
                'startTime': period.get('StartTime').split(':'),
                'endTime': period.get('EndTime').split(':')
            })
        timetable_week.append(timetable)
    
    
    # user_class_resources = intranet.class_resources(request)
    # user_classes = list()
    # for user_class in user_class_resources.get('Types')[0].get('TimetabledClasses'):
    #     class_name = user_class.get('SubjectDescription').lower()
    #     if class_name.endswith('assembly'):
    #         continue;
    #     elif class_name.endswith('pastoral care'):
    #         continue;
    #     user_classes.append(class_name)

    return render(request, 'calendar.html', {
        'user': user_information,
        'timetable': timetable_week
    })

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