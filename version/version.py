import boto3
import feedparser
import json
import os
from github import Github

def handler(event, context):

    try:
        poll_response = feedparser.parse('https://github.com/aws/aws-cdk/releases.atom')
    except:
        raise ValueError('RSS/Atom Feed Failure')  

    ssm_client = boto3.client('ssm')
    
    response = ssm_client.get_parameter(
        Name = os.environ['VERSIONS']
    )
    
    prevtoken = response['Parameter']['Value']

    if poll_response.entries[0].title != prevtoken:

        if poll_response.entries[0].title[0:2] == 'v2':

            lambda_client = boto3.client('lambda')

            lambda_client.invoke(
                FunctionName = os.environ['NEXT_LAMBDA'],
                InvocationType = 'Event',
                Payload = json.dumps('CDKBoot Install')
            )

            response = ssm_client.put_parameter(
                Name = os.environ['VERSIONS'],
                Value = poll_response.entries[0].title,
                Type = 'String',
                Overwrite = True
            )

    return {
        'statusCode': 200,
        'body': json.dumps('CDKBoot Version')
    }