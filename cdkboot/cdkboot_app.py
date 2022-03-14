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

class CdkbootApp(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

################################################################################

        qualifier = '4n6ir'                         # <-- Enter CDK Qualifier

        regions = 'us-east-1,us-east-2,us-west-2'   # <-- Enter Regions

################################################################################

        account = Stack.of(self).account
        region = Stack.of(self).region
        bootstrap_name = 'cdkboot-bootstrap-'+account+'-'+region

### Organization ID Parameter ###

        orgid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'orgid',
            parameter_name = '/cdkboot/orgid'
        ).string_value

### Bootstrap Bucket ###

        bootstrap = _s3.Bucket(
            self, 'bootstrap',
            bucket_name = bootstrap_name,
            versioned = True,
            encryption = _s3.BucketEncryption.S3_MANAGED,
            block_public_access = _s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy = RemovalPolicy.DESTROY
        )

        bucket_policy = _iam.PolicyStatement(
            effect = _iam.Effect(
                'ALLOW'
            ),
            principals = [
                _iam.AnyPrincipal()
            ],
            actions = [
                's3:GetObject'  
            ],
            resources = [
                bootstrap.bucket_arn+'/*'
            ],
            conditions = {"StringEquals": {"aws:PrincipalOrgID": orgid}}
        )
        bootstrap.add_to_resource_policy(bucket_policy)

### IAM Role

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

        role.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    'cloudformation:UpdateStack',
                    'iam:PassRole',
                    'organizations:ListAccounts',
                    's3:GetObject',
                    's3:PutObject',
                    'ssm:GetParameter',
                    'ssm:PutParameter',
                    'sts:AssumeRole'
                ],
                resources = ['*']
            )
        )

### GitHub RSS Feed ###

        install = _lambda.DockerImageFunction(
            self, 'install',
            code = _lambda.DockerImageCode.from_image_asset('install'),
            environment = dict(
                BOOTSTRAP = bootstrap.bucket_name
            ),
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

        installmonitor = _ssm.StringParameter(
            self, 'installmonitor',
            description = 'CDKBoot Install Monitor',
            parameter_name = '/cdkboot/monitor/install',
            string_value = '/aws/lambda/'+install.function_name,
            tier = _ssm.ParameterTier.STANDARD,
        )
