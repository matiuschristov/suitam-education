import http.client
import urllib.parse
from html.parser import HTMLParser
import json
import time
import socket
from pages import utils
from pages.exception import *
from datetime import datetime, timedelta, time

# function requestSuitam()
    # Arguments
        # host = the host for the request defaults to 'intranet.aquinas.vic.edu.au'
        # method = the HTTP method for the request
        # timeout = the timeout for the request defaults to 10
        # body = the body for the request only applicable if method is POST,PUT or PATCH
        # authentication = the cookie that stores the authentication token
        # connection = reuse an existing connection rather than start a new one (performance) not required
    # Description
        # the default wrapper function for making requests to the Aquinas SIMON server
    # Error Handling
        # SuitamException MISSING_REQUIRED_KEYWORD_ARG = when keyword arguments method,path are not passed in
        # SuitamException FAILED_AUTH = when the provided cookie authentication details are incorrect or expired
        # SuitamException HTTP_CONN_TIMEOUT = when the server does not respond within timeout
#
def requestSuitam(host='intranet.aquinas.vic.edu.au', method=None, path=None, timeout=10, body=None, headers=dict(), authentication=None, connection=None):
    if not connection:
        connection = http.client.HTTPSConnection(host, 443, timeout=timeout)
    if not method or not path:
        raise SuitamException('scraper.intranet.request: missing required keyword args', 'MISSING_REQUIRED_KEYWORD_ARG')
    try:
        req_headers = {
            'User-Agent': 'SuitamBot/1.0',
        }
        if body:
            req_headers['Content-Length'] = len(body)
        if authentication:
            req_headers['Cookie'] = authentication
        req_headers.update(headers)
        connection.request(method, path, body=body, headers=req_headers)
        res = connection.getresponse()
        if res.status == 401:
            raise SuitamException('scraper.intranet.request: request failed you are not authenticated', 'FAILED_AUTH')
        return {"response": res, "connection":connection};
    except socket.timeout:
        raise SuitamException('scraper.intranet.request: the connection timed out', 'HTTP_CONN_TIMEOUT')
    finally:
        if not connection:
            connection.close()

# function login()
    # Arguments
        # username = the username provided when user logs in
        # password = the password provided when user logs in
    # Description
        # log into the aquinas SIMON server returns a dictionary of cookies including the authentication token
    # Error Handling
        # inherit requestSuitam()
        # returns None if authentication failed
#
def login(username: str, password: str):
    req = requestSuitam(method='GET', path='/Login/Default.aspx')
    res = req and req.get('response')
    data = res and res.read()
    connection = req and req.get('connection')

    values_login = {
        '__VIEWSTATE': None,
        '__VIEWSTATEGENERATOR': None,
        '__VIEWSTATEENCRYPTED': None,
        '__EVENTVALIDATION': None,
        'Version': None,
        'buttonLogin': None,
        'clientScreenHeight': '864',
        'clientScreenWidth': '1512',
        'inputUsername': username,
        'inputPassword': password
    }

    def parse_input(input_value: dict):
        for value in values_login:
            if value == input_value.get('name') and input_value.get('value'):
                values_login[value] = input_value.get('value')

    class IntranetLoginParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'input':
                values = dict()
                for attr in attrs:
                    values[attr[0]] = attr[1]
                parse_input(values)
    parser = IntranetLoginParser()
    parser.feed(str(data))

    req = requestSuitam(method='POST', path='/Login/Default.aspx', body=urllib.parse.urlencode(values_login), connection=connection, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    res = req and req.get('response')
    res_headers = res.getheaders()
    connection.close()

    cookies = dict()
    if res.status == 302:
        for header in filter(lambda header: header[0] == 'Set-Cookie', res_headers):
            cookies[header[1].split('=')[0]] = header[1].split('=')[1].split('; ')[0]
        del cookies['ASP.NET_SessionId']
        return cookies
    else:
        return None

# function user_personal_details()
    # Arguments
        # request = the HttpResponse object which is supplied in the view function
        # id = the id of the user should be derrived from user_information()
    # Description
        # gets user personal details from the Aquinas SIMON server
    # Error Handling
        # inherit requestSuitam()
#
def user_personal_details(request, id) -> dict:
    req = requestSuitam(
        method='POST',
        path='/WebModules/Profiles/Student/StudentProfiles.asmx/StudentProfileDetails',
        body=json.dumps({'studentID':id}),
        headers={'Content-Type': 'application/json'},
        authentication=request.headers.get('Cookie')
    )
    res = req and req.get('response')
    data = json.loads(res.read()).get('d')
    (req and req.get('connection')).close()
    return data

# function user_dashboard_data()
    # Arguments
        # request = the HttpResponse object which is supplied in the view function
        # guidString = the guid of the user should be derrived from user_information()
    # Description
        # gets dashboard data from the Aquinas SIMON server
    # Error Handling
        # inherit requestSuitam()
#
def user_dashboard_data(request, guidString: str) -> dict:
    req = requestSuitam(
        method='POST',
        path='/WebModules/Profiles/Student/GeneralInformation/StudentDashboard.aspx/GetDashboardData?{}'.format(time.time() * 1000),
        body=json.dumps({"guidString":guidString,"semester":None}),
        headers={'Content-Type': 'application/json'},
        authentication=request.headers.get('Cookie')
    )
    res = req and req.get('response')
    data = json.loads(res.read()).get('d')
    (req and req.get('connection')).close()
    return data

# function user_navigation_menu()
    # Arguments
        # request = the HttpResponse object which is supplied in the view function
        # id = the id of the user should be derrived from user_information()
    # Description
        # gets user personal details from the Aquinas SIMON server
    # Error Handling
        # inherit requestSuitam()
#
def user_navigation_menu(request, id) -> dict:
    req = requestSuitam(
        method='POST',
        path='/WebModules/Profiles/Student/StudentProfiles.asmx/GetProfileNavigationMenuByStudentID',
        body=json.dumps({'studentID':id}),
        headers={'Content-Type': 'application/json'},
        authentication=request.headers.get('Cookie')
    )
    res = req and req.get('response')
    data = json.loads(res.read()).get('d')
    (req and req.get('connection')).close()
    return data

# function user_information()
    # Arguments
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # gets user information from the Aquinas SIMON server
        # data requested upon each authenticated request as it retrieves user details from auth cookie
    # Error Handling
        # inherit requestSuitam()
#
def user_information(request) -> dict:
    req = requestSuitam(
        method='POST',
        path='/Default.asmx/UserInformation',
        body='{}',
        headers={'Content-Type': 'application/json'},
        authentication=request.headers.get('Cookie')
    )
    res = req and req.get('response')
    data = json.loads(res.read()).get('d')
    (req and req.get('connection')).close()
    return data

# function class_resources()
    # Arguments
        # request = the HttpResponse object which is supplied in the view function
    # Description
        # gets user class resources which includes due,overdue,upcoming tasks from the Aquinas SIMON server
    # Error Handling
        # inherit requestSuitam()
#
def class_resources(request) -> dict:
    req = requestSuitam(
        method='POST',
        path='/Default.asmx/GetClassResources',
        body=json.dumps({"FileSeq":None,"UserID":None}),
        headers={'Content-Type': 'application/json'},
        authentication=request.headers.get('Cookie')
    )
    res = req and req.get('response')
    data = json.loads(res.read()).get('d')
    (req and req.get('connection')).close()
    return data

# function user_timetable()
    # Arguments
        # request = the HttpResponse object which is supplied in the view function
        # date = date object or None
    # Description
        # gets a user's timetable from the Aquinas SIMON server
    # Error Handling
        # inherit requestSuitam()
#
def user_timetable(request, date=None) -> dict:
    if not date:
        date = datetime.utcnow()
    date_current = date.isoformat(timespec='milliseconds') + 'Z';
    req = requestSuitam(
        method='POST',
        path='/Default.asmx/GetTimetable',
        body=json.dumps({"selectedDate":date_current,"selectedGroup":None}),
        headers={'Content-Type': 'application/json'},
        authentication=request.headers.get('Cookie')
    )
    res = req and req.get('response')
    data = json.loads(res.read()).get('d')
    (req and req.get('connection')).close()
    
    periods = []
    for period in data.get('Periods'):
        classes = period.get('Classes')
        if len(classes) == 0:
            continue;
        if not classes[0].get('Room'):
            continue;
        periods.append({
            'code': classes[0].get('TimeTableClass'),
            'name': utils.class_correct_capitalisation(classes[0].get('Description')),
            'teacher': classes[0].get('TeacherName'),
            'room': classes[0].get('Room'),
            'id': classes[0].get('ClassID'),
            'startTime': period.get('StartTime').split(':'),
            'endTime': period.get('EndTime').split(':')
        })

    return periods

# function user_photo()
    # Arguments
        # request = the HttpResponse object which is supplied in the view function
        # guidString = the guid of the user should be derrived from user_information()
    # Description
        # gets a buffer of the user's profile picture from the Aquinas SIMON server
    # Error Handling
        # inherit requestSuitam()
#
def user_photo(request, guidString) -> dict:
    req = requestSuitam(
        method='GET',
        path='/WebHandlers/DisplayUserPhoto.ashx?GUID={}'.format(guidString),
        authentication=request.headers.get('Cookie')
    )
    res = req and req.get('response')
    data = res.read()
    (req and req.get('connection')).close()
    return data