from aws_cdk import (
    CustomResource,
    Duration,
    RemovalPolicy,
    Stack,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_s3 as _s3,
    aws_ssm as _ssm,
    custom_resources as _custom
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
        bucket_name = 'cdkboot-bootstrap-'+account+'-'+region

### Organization ID Parameter ###

        orgid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'orgid',
            parameter_name = '/cdkboot/orgid'
        ).string_value

### Bootstrap Bucket ###

        bucket = _s3.Bucket(
            self, 'bucket',
            bucket_name = bucket_name,
            versioned = True,
            auto_delete_objects = True,
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
                bucket.bucket_arn+'/*'
            ],
            conditions = {"StringEquals": {"aws:PrincipalOrgID": orgid}}
        )
        bucket.add_to_resource_policy(bucket_policy)

### IAM Role ###

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
                    'secretsmanager:GetSecretValue',
                    'ssm:GetParameter',
                    'ssm:PutParameter',
                    'sts:AssumeRole'
                ],
                resources = ['*']
            )
        )

### Install Bootstrap ###

        bootstrap = _ssm.StringParameter(
            self, 'bootstrap',
            description = 'CDKBoot Bootstrap Version',
            parameter_name = '/cdkboot/bootstrap',
            string_value = 'Empty',
            tier = _ssm.ParameterTier.STANDARD
        )

        install = _lambda.DockerImageFunction(
            self, 'install',
            code = _lambda.DockerImageCode.from_image_asset('install'),
            environment = dict(
                BUCKET = bucket.bucket_name,
                BOOTSTRAP = bootstrap.parameter_name
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

        provider = _custom.Provider(
            self, 'provider',
            on_event_handler = install
        )

        resource = CustomResource(
            self, 'resource',
            service_token = provider.service_token
        )

### GitHub RSS Feed ###

        versions = _ssm.StringParameter(
            self, 'versions',
            description = 'CDKBoot Version',
            parameter_name = '/cdkboot/version',
            string_value = 'Empty',
            tier = _ssm.ParameterTier.STANDARD
        )

        version = _lambda.DockerImageFunction(
            self, 'version',
            code = _lambda.DockerImageCode.from_image_asset('version'),
            environment = dict(
                VERSIONS = versions.parameter_name
            ),
            timeout = Duration.seconds(900),
            memory_size = 512,
            role = role
        )

        versionlogs = _logs.LogGroup(
            self, 'versionlogs',
            log_group_name = '/aws/lambda/'+version.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )

        versionmonitor = _ssm.StringParameter(
            self, 'versionmonitor',
            description = 'CDKBoot Version Monitor',
            parameter_name = '/cdkboot/monitor/version',
            string_value = '/aws/lambda/'+version.function_name,
            tier = _ssm.ParameterTier.STANDARD,
        )

        event = _events.Rule(
            self, 'event',
            schedule=_events.Schedule.cron(
                minute='0',
                hour='*',
                month='*',
                week_day='*',
                year='*'
            )
        )
        event.add_target(_targets.LambdaFunction(version))

###
