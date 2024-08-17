import http.client
import urllib.parse
from html.parser import HTMLParser
import json
import time
import socket
from pages import utils
from pages.exception import *
from datetime import datetime

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

    class IntranetParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'input':
                values = dict()
                for attr in attrs:
                    values[attr[0]] = attr[1]
                parse_input(values)

        def handle_endtag(self, tag):
            pass
            # print("Encountered an end tag :", tag)

        def handle_data(self, data):
            pass
            # print("Encountered some data  :", data)

    parser = IntranetParser()
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

def user_timetable(request, date = datetime.utcnow()) -> dict:
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

def user_photo(request, guid) -> dict:
    print(guid)
    req = requestSuitam(
        method='GET',
        path='/WebHandlers/DisplayUserPhoto.ashx?GUID={}'.format(guid),
        authentication=request.headers.get('Cookie')
    )
    res = req and req.get('response')
    data = res.read()
    (req and req.get('connection')).close()
    return data