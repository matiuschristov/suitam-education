import http.client
import urllib.parse
from html.parser import HTMLParser
import json
import time
from datetime import datetime

def login(username: str, password: str):
    connection = http.client.HTTPSConnection('intranet.aquinas.vic.edu.au', 443, timeout=10)
    connection.request('GET', '/Login/Default.aspx')
    response = connection.getresponse()
    print("Status: {} and reason: {}".format(response.status, response.reason))
    data = response.read()

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
    data = urllib.parse.urlencode(values_login)

    connection.request('POST', '/Login/Default.aspx', body=data, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': len(data),
        'User-Agent': 'SuitamBot/1.0'
    })

    authResponse = connection.getresponse()
    authHeaders = authResponse.getheaders()

    authCookies = dict()
    
    if authResponse.status == 302:
        for header in filter(lambda header: header[0] == 'Set-Cookie', authHeaders):
            authCookies[header[1].split('=')[0]] = header[1].split('=')[1].split('; ')[0]
        return authCookies
    else:
        return None
    
def user_personal_details(request) -> dict:
    connection = http.client.HTTPSConnection('intranet.aquinas.vic.edu.au', 443, timeout=50)
    connection_data = json.dumps({'studentID':'4972'})
    connection.request('POST', '/WebModules/Profiles/Student/StudentProfiles.asmx/StudentProfileDetails', body=connection_data, headers={
        'Content-Length': len(connection),
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('Cookie'),
        'User-Agent': 'SuitamBot/1.0'
    })
    response = connection.getresponse()
    data = json.loads(response.read()).get('d')
    return data

def user_dashboard_data(request, guidString: str) -> dict:
    connection = http.client.HTTPSConnection('intranet.aquinas.vic.edu.au', 443, timeout=50)
    connection_data = json.dumps({"guidString":guidString,"semester":None})
    connection.request('POST', '/WebModules/Profiles/Student/GeneralInformation/StudentDashboard.aspx/GetDashboardData?{}'.format(time.time() * 1000), body=connection_data, headers={
        'Content-Length': len(connection_data),
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('Cookie'),
        'User-Agent': 'SuitamBot/1.0'
    })
    response = connection.getresponse()
    data = json.loads(response.read()).get('d')
    return data

def user_navigation_menu(request) -> dict:
    connection = http.client.HTTPSConnection('intranet.aquinas.vic.edu.au', 443, timeout=50)
    connection_data = json.dumps({'studentID':'4972'})
    connection.request('POST', '/WebModules/Profiles/Student/StudentProfiles.asmx/GetProfileNavigationMenuByStudentID', body=connection_data, headers={
        'Content-Length': len(connection_data),
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('Cookie'),
        'User-Agent': 'SuitamBot/1.0'
    })
    response = connection.getresponse()
    data = json.loads(response.read()).get('d')
    return data
    
def user_information(request) -> dict:
    connection = http.client.HTTPSConnection('intranet.aquinas.vic.edu.au', 443, timeout=50)
    connection_data = '{}'
    connection.request('POST', '/Default.asmx/UserInformation', body=connection_data, headers={
        'Content-Length': len(connection_data),
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('Cookie'),
        'User-Agent': 'SuitamBot/1.0'
    })

    response = connection.getresponse()
    data = json.loads(response.read()).get('d')
    return data

def class_resources(request) -> dict:
    connection = http.client.HTTPSConnection('intranet.aquinas.vic.edu.au', 443, timeout=50)
    connection_data = json.dumps({"FileSeq":None,"UserID":None})
    connection.request('POST', '/Default.asmx/GetClassResources', body=connection_data, headers={
        'Content-Length': len(connection_data),
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('Cookie'),
        'User-Agent': 'SuitamBot/1.0'
    })

    response = connection.getresponse()
    # print("Status: {} and reason: {}".format(response.status, response.reason))
    data = json.loads(response.read()).get('d')
    return data

def user_timetable(request, date = datetime.utcnow()) -> dict:
    # https://intranet.aquinas.vic.edu.au/Default.asmx/GetTimetable
    # week_timetable = [];
    # for day in enumerate(7)
    date_current = date.isoformat(timespec='milliseconds') + 'Z';
    # date_current = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z';
    # date_current = datetime(2024, 8, 8).date().isoformat(timespec='milliseconds') + 'Z';
    connection = http.client.HTTPSConnection('intranet.aquinas.vic.edu.au', 443, timeout=50)
    connection_data = json.dumps({"selectedDate":date_current,"selectedGroup":None})
    connection.request('POST', '/Default.asmx/GetTimetable', body=connection_data, headers={
        'Content-Length': len(connection_data),
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('Cookie'),
        'User-Agent': 'SuitamBot/1.0'
    })

    response = connection.getresponse()
    data = json.loads(response.read()).get('d')
    return data

def user_photo(request) -> dict:
    if not request.headers.get('Cookie'):
        raise Exception('Request cookie is required')

    data_user = user_information(request)

    connection = http.client.HTTPSConnection('intranet.aquinas.vic.edu.au', 443, timeout=50)
    connection.request('GET', '/WebHandlers/DisplayUserPhoto.ashx?GUID={}'.format(data_user.get('guid')), body='{}', headers={'Cookie': request.headers.get('Cookie'), 'User-Agent': 'SuitamBot/1.0'})

    response = connection.getresponse()
    data = response.read()
    return data