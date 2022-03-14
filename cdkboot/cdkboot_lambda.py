from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_s3 as _s3,
    aws_ssm as _ssm
)

from constructs import Construct

from aws_cdk.aws_lambda import Function, InlineCode, Runtime

class CdkbootLambda(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role = _iam.Role(
            self, 'role', 
            assumed_by = _iam.ServicePrincipal(
                'lambda.amazonaws.com'
            )
        )

        role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaBasicExecutionRole'
            )
        )

        install = _lambda.DockerImageFunction(
            self, 'install',
            code = _lambda.DockerImageCode.from_image_asset('install'),
            timeout = Duration.seconds(900),
            memory_size = 512,
            role = role
        )

        installlogs = _logs.LogGroup(
            self, 'installlogs',
            log_group_name = '/aws/lambda/'+install.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )
