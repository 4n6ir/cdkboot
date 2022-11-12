import aws_cdk as cdk

from aws_cdk import Stack

from aws_cdk.pipelines import (
    CodePipeline,
    CodePipelineSource,
    ShellStep
)

from constructs import Construct

from cdkboot.cdkboot_stage import CdkbootStage

class CdkbootStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account = Stack.of(self).account
        region = Stack.of(self).region

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

        pipeline.add_stage(
            CdkbootStage(
                self, 'cdkboot',
                env = cdk.Environment(
                    account = account,
                    region = region
                )
            )
        )


