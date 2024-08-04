 
I
Designing an Automatic Data Collection and Storage System with AWS Lambda and Slack Integration for Server Availability Monitoring and Slack Notification


mage courtesy-https://slack.com/intl/en-in/blog/collaboration/aws-chatbot-bring-aws-into-your-slack-channel

Designing an Automatic Data Collection and Storage System with AWS Lambda and Slack Integration for Server Availability Monitoring and Slack Notification using AWS Lambda, CloudWatch, Slack API.
Creating a AWS Lambda function for fetching the data from the API.
Creating a trigger in cloudwatch every minute, if API server goes down ,it will send a slack notification.
Creating a Lambda function for fetching the data (Lambda-1)
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
 
 
Downloading the essential packages for the function in lambda layers
I have chosen the tokyo data center and the packages in specific data center were taken for creating layer (link to get the packages )
 
I have added requests and psycopg2 packages to the layer.
 
Lambda function to fetch data from Api.
import psycopg2
import psycopg2.extras as extras
import requests
import json

def lambda_handler(event, context):
    # TODO implement
    
    server_status = False
    
    try:
        api = requests.get('http://api.open-notify.org/iss-now.json')
        data = json.loads(api.content)
        timestamp = data['timestamp']
        message_status = data['message']
        longitude_data = data['iss_position']['longitude']
        latitude_data = data['iss_position']['latitude']
        if message_status == "success":
            server_status = True
    except requests.exceptions.RequestException as e: 
        pass
        
    
    if server_status:
        conn = psycopg2.connect(
            host = 'database.h3axyzj0mace.ap-northeast-1.rds.amazonaws.com',
            port = 5432,
            user = 'username',
            password = 'ayx246',
            database = 'project'
        )
        
        cols = 'timestamp,message_status,longitude_data,latitude_data'
        data = [(timestamp, message_status, longitude_data, latitude_data)]
        query = "INSERT INTO %s(%s) VALUES %%s" % ('slack_data', cols)
        cursor = conn.cursor()
    
        try:
            extras.execute_values(cursor, query, data)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            cursor.close()
        print("the dataframe is inserted")
        cursor.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps('Data saved in RDS')
        }
    else:
        raise Exception('Failed')
AWS Lambda function that fetches data from the API, specifying the current position of the International Space Station (ISS). It checks the server status by making an HTTP request and extracts relevant data such as the timestamp, message status, longitude, and latitude.
If the request is successful and the message status is “success,” the server status is set to True. The code then establishes a connection to a PostgreSQL database and inserts the retrieved data into a table called slack data. Finally, it returns a response indicating the success of the operation or raises an exception if the server status is False, indicating a failed API request.
Deploy and test the function to check the function.
Go to https://api.slack.com/apps/new and create a new app in slack workspace
 
 
 
Copy the webhook url and paste in lambda — 2 function for Sending Server Error Notifications to Slack.
AWS Lambda Function for Sending Server Error Notifications to Slack (Lambda -2 )
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
AWS Lambda function that sends a server error notification to a Slack channel using a webhook. It prepares a Slack message with the text “Server error” and sends it to the specified webhook URL. If successful, it prints a confirmation message otherwise, it prints the corresponding error message.
Creating a SNS Topic
SNS triggers lambda-2 to create slack notification
 
Create a SNS topic
 
Creating a SNS trigger in lambda
 
 
Cloudwatch alarm
Cloud-alarm triggers based on lambda-1 failure (if the server goes down)
 
Go to cloudwatch alarm and select metric → Lambda → By function Name
 
functionName — slack_final_project( Lambda -2)
 
Set threshold value for error even if one time the server goes down in a minute, the cloudwatch alarm will display
 
Select SNS topic
 
Add alarm name and create cloudwatch alarm
Testing Our Application
Let’s manually fail the function to check if the function is working, because if the server is fine there will be no notification in the slack app
#Make the server fail by modifying this code in Lambda-1 if not statement does the work
if not server_status:
        conn = psycopg2.connect(
            host = 'database.h3axyzj0mace.ap-northeast-1.rds.amazonaws.com',
            port = 5432,
            user = 'username',
            password = 'ayx246',
            database = 'project'
        )
 
The small blue dots indicate the server failure, which will direct the lambda-2 through SNS to generate a slack notification
 

