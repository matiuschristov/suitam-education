from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from scraper import intranet
from pages import utils
from pages.decorators import *
import json
import random
import urllib

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
        auth_redirect = redirect('/overview/')
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
    
    user_class_resources = intranet.class_resources(request)
    user_classes = list()
    for user_class in user_class_resources.get('Types')[0].get('TimetabledClasses'):
        user_classes.append(user_class.get('SubjectDescription'))

    def correct_capitalisation(subject):
        subject = subject.lower().split(' ')
        del subject[0:2]
        updated = list()
        keepLowerCase = ['and', 'at']
        for x in subject:
            if x == 'pe':
                updated.append(x.upper())
            elif x == 'it' or x == 'it:':
                updated.append(x.upper())
            elif [match for match in keepLowerCase if x in match]:
                updated.append(x)
            else:
                updated.append(x.title())
        return " ".join(updated)

    return render(request, 'overview.html', {
        'user': user_information,
        'classes': list(map(correct_capitalisation, user_classes))
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
        # '\n'.join(user_classes)
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