#!/usr/bin/python

import requests
from datetime import datetime
import time

def parse_date(d_string):
    date_format = "%Y-%m-%d %H:%M:%S"

    try:
        d_sanitized = d_string.split('.')[0].replace("T", " ")
        time_tuple = datetime.strptime(d_sanitized, date_format).timetuple()
    except:
        print "Exception"
        print d_string.replace("T", " ")
        return None

    return int(time.mktime(time_tuple))

#Apica ASM (WPM) Auth Ticket - GUID (e.g 00000000-AAAA-0000-AAAA-000000000000)
wpm_auth_ticket = ''
#Apica API Base URL e.g api-wpm1, api-wpmN, ...
wpm_base_url = 'https://api-wpm1.apicasystem.com/v3/'

panda_base_url = "https://api.bigpanda.io/data/v2/"
panda_auth_token = ""
panda_app_key = ""

panda_auth_header = {"Authorization": "Bearer " + panda_auth_token}
post_base = {"app_key": panda_app_key}
panda_sev_map = {
	"I": "ok",
	"W": "warning",
	"E": "critical",
	"F": "critical"
}

most_recent_data = {}
check_ids = {}

for check_data in requests.get(wpm_base_url + 'checks?enabled=1&auth_ticket=' + wpm_auth_ticket).json():
    check_ids[check_data.get('id')] = check_data.get('name')

for id in check_ids.keys():
    # {u'severity': u'I', u'check_id': 111730, u'timestamp_utc': u'2017-02-27T18:24:16', u'value': 773, u'attempts': 1,
    # u'unit': u'ms', u'message': u'1 url, 528/355 sent/received bytes.',
    #  u'identifier': u'9cb3e45b-a36f-40c4-109b-7efd3aa50ad2', u'result_code': 0}
    most_recent_http = requests.get(wpm_base_url + 'checks/{0}/results?mostrecent=1&detail_level=1&auth_ticket={1}'.format(id, wpm_auth_ticket))

    try:
        most_recent_result = most_recent_http.json()[0]
    except IndexError as ie:
        continue

    this_timestamp = parse_date(most_recent_result.get('timestamp_utc'))

    this_post_data = post_base.copy()
    this_post_data['timestamp'] = this_timestamp
    this_post_data['check'] = id
    this_post_data['description'] = check_ids[id]
    this_post_data['host'] = check_ids[id]
    this_post_data['status'] = panda_sev_map[most_recent_result.get('severity', 'I')]

    panda_post = requests.post(panda_base_url + 'alerts', headers=panda_auth_header, json=dict(this_post_data))

    if panda_post.status_code != 201:
        print("There may have been an error posting to bigpanda alert API.")
        print("HTTP Status: " + str(panda_post.status_code))
        print("Content: " + str(panda_post.content))


