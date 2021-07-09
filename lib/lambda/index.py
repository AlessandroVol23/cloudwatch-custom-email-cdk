
import json
import os
from typing import Dict

import boto3

ses = boto3.client('ses')

SOURCE_EMAIL = os.environ.get("SOURCE_EMAIL")
DESTINATION_EMAIL = os.environ.get("DESTINATION_EMAIL")


def handler(event, context):
    print("Event: ", event)
    records = event.get('Records')
    first_record = records[0]

    sns_message = first_record.get('Sns')

    html = fill_html_file(sns_message)

    send_email(html)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def fill_html_file(sns_message):
    message = json.loads(sns_message.get('Message'))
    alarm_name = message.get('AlarmName')
    account_id = message.get('AWSAccountId')
    reason = message.get('NewStateChangeReason')

    style = """<!DOCTYPE html>
    <html lang="en">

    <style>
    body {
        background-color: #ffffff;
        font-family: Arial, Helvetica, sans-serif;
    }

    .container {
        max-width: 680px;
        width: 100%;
        margin: auto;
    }

    main {
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        color: #555555;
    }

    .body h2 {
        font-weight: 300;
        color: #464646;
    }

    .logo {
        width: 150px;
        padding: 5px 5px;
    }

    .header-img {
        max-width: 100% !important;
        height: auto !important;
        width: 100%;
    }

    a {
        text-decoration: underline;
        color: #0c99d5;
    }

    .body {
        padding: 20px;
        background-color: rgba(228, 123, 17, 0.397);
        font-family: Geneva, Tahoma, Verdana, sans-serif;
        font-size: 16px;
        line-height: 22px;
        color: #555555;
        border-radius: 5%;
    }

    button {
        background-color: #d5950c;
        border: none;
        color: white;
        border-radius: 2px;
        height: 50px;
        max-width: 250px;
        padding: 0px 30px;
        font-weight: 500;
        font-family: Geneva, Tahoma, Verdana, sans-serif;
        font-size: 16px;
        margin: 10px 0px 30px 0px;
        cursor: pointer;
    }

    </style>
    """

    body = """
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Email</title>
    </head>

    <body>
    <main class="container">
        <div class="logo">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Amazon_Web_Services_Logo.svg/2880px-Amazon_Web_Services_Logo.svg.png" class="logo">
        </div>

        <div class="body">
        <h2>Cloudwatch Alarm!</h2>

        <p>Alarm Name: {}</p>
        <p>Account ID: {}</p>
        <p>Reason: {}</p>


        <a target="_blank" href="https://eu-central-1.console.aws.amazon.com/cloudwatch/home?region=eu-central-1#">
            <button>GO TO CLOUDWATCH</button>
        </a>

        </div>

    </main>


    </div>


    </body>

    </html>""".format(alarm_name, account_id, reason)

    return style + body


def send_email(html) -> Dict:
    response = ses.send_email(
        Source=SOURCE_EMAIL,
        Destination={'ToAddresses': [DESTINATION_EMAIL]},
        Message={
            'Subject': {
                'Data': 'New CloudWatch alarm.',
                'Charset': 'utf-8'
            },
            'Body': {
                'Html': {
                    'Data': html,
                    'Charset': 'utf-8'

                }
            }
        }
    )
    return response
