import aws_cdk as cdk

from constructs import Construct

from cdkboot.cdkboot_lambda import CdkbootLambda

class CdkbootStage(cdk.Stage):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambdaStack = CdkbootLambda(
            self, 'lambdaStack',
            synthesizer = cdk.DefaultStackSynthesizer(
                qualifier = '4n6ir'
            )
        )
