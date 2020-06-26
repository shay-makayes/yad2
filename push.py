from pushover import init, Client
import requests
import json

user_key = 'USER_KEY'
headers = {'Access-Token': user_key,
           'Content-Type': 'application/json'}
data = {"body": "Found new app!", "title": "New Apartment", 'url':'https://www.google.com',
        "type": "link"}
resp = requests.post(url='https://api.pushbullet.com/v2/pushes', headers=headers, data=json.dumps(data))
print(resp.status_code)
print(resp.text)
