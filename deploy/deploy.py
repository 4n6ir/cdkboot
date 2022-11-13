import boto3
import json
import os

def handler(event, context):

    cfn_client = boto3.client('cloudformation')

    paginator = cfn_client.get_paginator('list_stack_sets')

    pages = paginator.paginate(
        Status = 'ACTIVE',
        CallAs = 'DELEGATED_ADMIN'
    )

    for page in pages:
        for summary in page['Summaries']:
            if summary['StackSetName'].startswith('cdk-bootstrap-4n6ir-us-east-1'):
                print(summary)
                output = cfn_client.describe_stack_set(
                    StackSetName = summary['StackSetName'],
                    CallAs = 'DELEGATED_ADMIN'
                )
                status = cfn_client.update_stack_set(
                    StackSetName = summary['StackSetName'],
                    TemplateURL = 'https://'+os.environ['BUCKET']+'.s3.'+os.environ['REGION']+'.amazonaws.com/cdk.yaml',
                    Capabilities = ['CAPABILITY_NAMED_IAM'],
                    ExecutionRoleName = output['StackSet']['ExecutionRoleName'],
                    CallAs = 'DELEGATED_ADMIN',
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
                print(status)

    return {
        'statusCode': 200,
        'body': json.dumps('CDKBoot Deploy')
    }