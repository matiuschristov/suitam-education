import urllib.parse
from django.shortcuts import render, redirect
from django.http import HttpResponse
import urllib
from scraper import intranet
from pages import utils
from pages.exception import *

def e_500(error=None):
    return HttpResponse(error if error else 'An internal error occured please try again', status=500, headers={'Content-Type': 'text/plain'})

def require_authentication(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        if not request.COOKIES.get('adAuthCookie'):
            return redirect('/auth/login/?code=AUTH-REQUIRED')
        else:
            try:
                user = intranet.user_information(request)
                return func(*args, user)
            except SuitamException as e:
                if (e.error_code == 'FAILED_AUTH'):
                    res = redirect('/auth/login/?code=SESSION-EXPIRED')
                    utils.delete_cookie(res, 'adAuthCookie')
                    return res
                return e_500(error=e)
            except:
                return e_500()
                

    return wrapper