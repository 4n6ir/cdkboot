from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_s3 as _s3,
    aws_s3_notifications as _notifications,
    aws_ssm as _ssm
)

from constructs import Construct

class CdkbootApp(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

################################################################################

        qualifier = '4n6ir'                         # <-- Enter CDK Qualifier

################################################################################

        account = Stack.of(self).account
        region = Stack.of(self).region
        bucket_name = 'cdkboot-bootstrap-'+account+'-'+region

### Organization ID Parameter ###

        orgid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'orgid',
            parameter_name = '/cdkboot/orgid'
        ).string_value

### Account IDs Parameter ###

        acctids = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'acctids',
            parameter_name = '/cdkboot/acctids'
        ).string_value

### LAMBDA LAYER ###

        feedparser = _lambda.LayerVersion.from_layer_version_arn(
            self, 'feedparser',
            layer_version_arn = 'arn:aws:lambda:'+region+':070176467818:layer:feedparser:1'
        )

        getpublicip = _lambda.LayerVersion.from_layer_version_arn(
            self, 'getpublicip',
            layer_version_arn = 'arn:aws:lambda:'+region+':070176467818:layer:getpublicip:9'
        )

        pygithub = _lambda.LayerVersion.from_layer_version_arn(
            self, 'pygithub',
            layer_version_arn = 'arn:aws:lambda:'+region+':070176467818:layer:pygithub:1'
        )

### Bootstrap Bucket ###

        bucket = _s3.Bucket(
            self, 'bucket',
            bucket_name = bucket_name,
            encryption = _s3.BucketEncryption.S3_MANAGED,
            block_public_access = _s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy = RemovalPolicy.DESTROY,
            auto_delete_objects = True,
            enforce_ssl = True,
            versioned = True
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
                    'cloudformation:DescribeStackSet',
                    'cloudformation:ListStackSets',
                    'cloudformation:UpdateStackSet',
                    'iam:PassRole',
                    'organizations:ListDelegatedAdministrators',
                    'organizations:ListDelegatedServicesForAccount',
                    's3:GetObject',
                    's3:PutObject',
                    'secretsmanager:GetSecretValue',
                    'ssm:GetParameter',
                    'ssm:PutParameter'
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
            code = _lambda.DockerImageCode.from_image_asset(
                'install',
                build_args = {
                    'NOCACHE': '--no-cache'
                }
            ),
            environment = dict(
                AWS_ACCOUNT = account,
                BUCKET = bucket.bucket_name,
                BOOTSTRAP = bootstrap.parameter_name
            ),
            timeout = Duration.seconds(900),
            memory_size = 2048,
            role = role
        )

        installlogs = _logs.LogGroup(
            self, 'installlogs',
            log_group_name = '/aws/lambda/'+install.function_name,
            retention = _logs.RetentionDays.ONE_MONTH,
            removal_policy = RemovalPolicy.DESTROY
        )

        installmonitor = _ssm.StringParameter(
            self, 'installmonitor',
            description = 'CDKBoot Install Monitor',
            parameter_name = '/cdkboot/monitor/install',
            string_value = '/aws/lambda/'+install.function_name,
            tier = _ssm.ParameterTier.STANDARD,
        )

        events = _events.Rule(
            self, 'events',
            schedule = _events.Schedule.cron(
                minute = '0',
                hour = '*',
                month = '*',
                week_day = '*',
                year = '*'
            )
        )

        events.add_target(
            _targets.LambdaFunction(
                install
            )
        )

### GitHub RSS Feed ###

        versions = _ssm.StringParameter(
            self, 'versions',
            description = 'CDKBoot Version',
            parameter_name = '/cdkboot/version',
            string_value = 'Empty',
            tier = _ssm.ParameterTier.STANDARD
        )

        version = _lambda.Function(
            self, 'version',
            runtime = _lambda.Runtime.PYTHON_3_11,
            code = _lambda.Code.from_asset('version'),
            handler = 'version.handler',
            architecture = _lambda.Architecture.ARM_64,
            environment = dict(
                AWS_ACCOUNT = account,
                VERSIONS = versions.parameter_name
            ),
            timeout = Duration.seconds(900),
            memory_size = 512,
            role = role,
            layers = [
                feedparser,
                getpublicip,
                pygithub
            ]
        )

        versionlogs = _logs.LogGroup(
            self, 'versionlogs',
            log_group_name = '/aws/lambda/'+version.function_name,
            retention = _logs.RetentionDays.ONE_MONTH,
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
            schedule = _events.Schedule.cron(
                minute = '0',
                hour = '*',
                month = '*',
                week_day = '*',
                year = '*'
            )
        )

        event.add_target(
            _targets.LambdaFunction(
               version
           )
        )

### Deploy Cloud Formation ###

        deploy = _lambda.Function(
            self, 'deploy',
            runtime = _lambda.Runtime.PYTHON_3_11,
            code = _lambda.Code.from_asset('deploy'),
            handler = 'deploy.handler',
            architecture = _lambda.Architecture.ARM_64,
            environment = dict(
                AWS_ACCOUNT = account,
                ACCOUNT = acctids,
                BUCKET = bucket.bucket_name,
                QUALIFIER = qualifier,
                REGION = region
            ),
            timeout = Duration.seconds(900),
            memory_size = 512,
            role = role,
            layers = [
                getpublicip
            ]
        )

        deploylogs = _logs.LogGroup(
            self, 'deploylogs',
            log_group_name = '/aws/lambda/'+deploy.function_name,
            retention = _logs.RetentionDays.ONE_MONTH,
            removal_policy = RemovalPolicy.DESTROY
        )

        deploymonitor = _ssm.StringParameter(
            self, 'deploymonitor',
            description = 'CDKBoot Deploy Monitor',
            parameter_name = '/cdkboot/monitor/deploy',
            string_value = '/aws/lambda/'+deploy.function_name,
            tier = _ssm.ParameterTier.STANDARD,
        )

        notify = _notifications.LambdaDestination(deploy)
        bucket.add_event_notification(_s3.EventType.OBJECT_CREATED, notify)
