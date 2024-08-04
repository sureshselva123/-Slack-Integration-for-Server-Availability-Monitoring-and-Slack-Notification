import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import boto3

def lambda_handler(event,context):
    slack_message = {'text' : 'Server error'}
    webhook_url = "https://hooks.slack.com/services/"

    req = Request(webhook_url, json.dumps(slack_message).encode('utf-8'))
    
    try:
        response = urlopen(req)
        response.read()
        print("Messge posted to Slack")
    except HTTPError as e:
        print(f'Request failed: {e.code} {e.reason}')
    except URLError as e:
        print(f'Server Connection failed:  {e.reason}')