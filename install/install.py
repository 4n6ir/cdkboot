import boto3
import json
import os
import yaml

def handler(event, context):
    
    os.system('export CDK_NEW_BOOTSTRAP=1 && cdk bootstrap --show-template > /tmp/cdk.yaml')
    
    with open('/tmp/cdk.yaml', 'r') as stream:
        parsed_yaml = yaml.safe_load(stream)
    stream.close()
    
    ssm_client = boto3.client('ssm')
    
    response = ssm_client.get_parameter(
        Name = os.environ['BOOTSTRAP']
    )
    bootstrap = response['Parameter']['Value']

    if bootstrap != str(parsed_yaml['Resources']['CdkBootstrapVersion']['Properties']['Value']):

        s3_client = boto3.client('s3')

        s3_client.upload_file('/tmp/cdk.yaml', os.environ['BUCKET'], 'cdk.yaml')

        ssm_client.put_parameter(
            Name = os.environ['BOOTSTRAP'],
            Value = str(parsed_yaml['Resources']['CdkBootstrapVersion']['Properties']['Value']),
            Type = 'String',
            Overwrite = True
        )

    return {
        'statusCode': 200,
        'body': json.dumps('CDKBoot Install')
    }