import requests, json
from datadog import initialize, api
from datadog.api.constants import CheckStatus

##Proxy Definition
proxies = {
    'http':'http://proxy.server.com:8080',
    'https':'http://proxy.server.com:8080'
}

##DataDog App Key
dd_options = {
  'api_key': '00000aaaaaa00000a0a00a00a000',
  'app_key': '00000aaaaaa00000a0a00a00a000',
  'proxies': proxies
}

#Apica API Base URL e.g api-wpm1, api-wpm2, api-wpm{{n}}, ...
apica_api = 'https://api-wpm1.apicasystem.com/v3/'

#Apica ASM (WPM) Auth Ticket - GUID (e.g 00000000-AAAA-0000-AAAA-000000000000)
auth_ticket = ''


initialize(**dd_options)

def build_route(*args):
  route = apica_api + args[0] + '?auth_ticket='+args[1]
  if len(args) > 2:
    return +'&'+args[2]
  else:
    return route

def get_history():
  try:
    with open('checkhistory.json','r') as hist:
      checks = json.loads(hist.read())
  except Exception as e:
    checks = []
  return checks

def write_checks(checks):
  with open('checkhistory.json', 'w') as hist:
    hist.write(json.dumps(checks))

def get_failures(checks):
  i_checks = (x for x in checks if (x['severity'] == 'F' and 'TEST' not in x['name'] and x['enabled']))
  c_failures = list()
  for x in i_checks:
    c_failures.append(x['id'])
  return c_failures

def send_alarm(item, status):
  tags=[
    'name:'+item['name'],
    'url:https://wpm.apicasystem.com/Check/Details/'+str(item['id'])
  ]
  values = item['name'].split('|')
  if len(values) == 6:
    tags.append('location:'+values[0])
    tags.append('group:'+values[1])
    tags.append('identifier:'+values[2])
    tags.append('environment:'+values[3])
    tags.append('type:'+values[4])
    tags.append('target_url:'+values[5])
  api.ServiceCheck.check(check='apica.status',host_name='wpm.apicasystem.com',status=status,tags=tags)
  print str(item['id'])+':'+str(status)+':'+str(len(tags))

route = build_route('checks',auth_ticket)
r = requests.get(route,proxies=proxies)
checks = r.json()

c_failures = get_failures(checks)
h_failures = get_history()

c_hist = list()

i_checks = (x for x in checks if x['id'] in c_failures)
for check in i_checks:
  if check['id'] not in h_failures: send_alarm(check, CheckStatus.CRITICAL)
  c_hist.append(check['id'])

for check_id in h_failures:
  if check_id not in c_failures: send_alarm(check, CheckStatus.OK)

write_checks(c_hist)
