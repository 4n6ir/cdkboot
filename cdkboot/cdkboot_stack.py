from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack
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
            )
        )
