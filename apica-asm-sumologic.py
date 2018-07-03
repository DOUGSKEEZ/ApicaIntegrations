import requests
import os

headers = {'Content-Type': 'application/json'}

#Use API endpoint that you want to pull data from
url = 'https://api-wpm.apicasystem.com/v3/Checks/#############?auth_ticket=#############################'

send = requests.get(url).content

with open("./wpmdata", 'w') as datafile:
    datafile.write(send)

## Replace endpoint with your sumo endpoint
sumourl = 'https://endpoint1.collection.us2.sumologic.com/receiver/v1/http/############################################################################################'


files = {'file': open('wpmdata','rb')}

sumoresp = requests.post(sumourl, files=files)

print sumoresp.content
print sumoresp.status_code