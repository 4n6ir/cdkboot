from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs
)

from aws_cdk.pipelines import (
    CodePipeline,
    CodePipelineSource,
    ShellStep
)

from constructs import Construct

class CdkbootStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        pipeline = CodePipeline(
            self, 'pipeline', 
            synth = ShellStep(
                'Synth', 
                input = CodePipelineSource.git_hub(
                    'jblukach/cdkboot',
                    'main'
                ),
                commands = [
                    'npm install -g aws-cdk', 
                    'python -m pip install -r requirements.txt', 
                    'cdk synth'
                ]
            ),
            docker_enabled_for_synth = True
        )

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
