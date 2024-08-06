import urllib.parse
from django.shortcuts import render, redirect
from django.http import HttpResponse
import urllib

def require_authentication(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        if not request.COOKIES.get('ASP.NET_SessionId') and not request.COOKIES.get('adAuthCookie'):
            # .format(urllib.parse.quote(request.get_full_path(), safe=''))
            return redirect('/auth/login/')
        else:
            return func(*args, **kwargs)
    return wrapper