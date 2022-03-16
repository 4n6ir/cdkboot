import boto3
import json
import os

def handler(event, context):

### CREATE ACCOUNT LIST ###

    accounts = []

    try:

        org_client = boto3.client('organizations')

        paginator = org_client.get_paginator('list_accounts')

        response_iterator = paginator.paginate()

        for page in response_iterator:
            for item in page['Accounts']:
                if item['Status'] == 'ACTIVE':
                    accounts.append(str(item['Id']))

    except:
        
        accounts.append(os.environ['ACCOUNT'])
        
        pass

### CREATE/UPDATE CDK BOOTSTRAPS ###

    sts_role = boto3.client('sts')

    for account in accounts:
                
        regions = os.environ['REGIONS'].split(',')
                
        for region in regions:
                    
            arn_role = 'arn:aws:iam::'+str(account)+':role/cdk-'+os.environ['QUALIFIER']+'-deploy-role-'+str(account)+'-'+region
            exe_role = 'arn:aws:iam::'+str(account)+':role/cdk-'+os.environ['QUALIFIER']+'-cfn-exec-role-'+str(account)+'-'+region
                    
            response = sts_role.assume_role(
                RoleArn = arn_role,
                RoleSessionName = 'cdkboot-'+str(account)+'-'+region,
            )
                
            sts_assumed_role = boto3.client(
                'cloudformation', region_name = region,
                aws_access_key_id = response['Credentials']['AccessKeyId'],
                aws_secret_access_key = response['Credentials']['SecretAccessKey'],
                aws_session_token = response['Credentials']['SessionToken']
            )
                    
            try:
                sts_assumed_role.update_stack(
                    StackName = 'cdk-bootstrap-'+os.environ['QUALIFIER']+'-'+str(account)+'-'+region,
                    TemplateURL = 'https://'+os.environ['BUCKET']+'.s3.'+os.environ['REGION']+'.amazonaws.com/cdk.yaml',
                    Capabilities = ['CAPABILITY_NAMED_IAM'],
                    RoleARN = exe_role,
                    Parameters = [
                        {
                            'ParameterKey': 'CloudFormationExecutionPolicies',
                            'ParameterValue': 'arn:aws:iam::aws:policy/AdministratorAccess'
                        },
                        {
                            'ParameterKey': 'FileAssetsBucketKmsKeyId',
                            'ParameterValue': 'AWS_MANAGED_KEY'
                        },
                        {
                            'ParameterKey': 'PublicAccessBlockConfiguration',
                            'ParameterValue': 'true'
                        },
                        {
                            'ParameterKey': 'Qualifier',
                            'ParameterValue': os.environ['QUALIFIER']
                        },
                        {
                            'ParameterKey': 'TrustedAccounts',
                            'ParameterValue': os.environ['ACCOUNT']
                        }
                    ]
                )
                print('UPDATED: '+str(account)+' '+region)
            except:
                print('NO NEED: '+str(account)+' '+region)

    return {
        'statusCode': 200,
        'body': json.dumps('CDKBoot Deploy')
    }