import aws_cdk as cdk

from constructs import Construct

from cdkboot.cdkboot_app import CdkbootApp

class CdkbootStage(cdk.Stage):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        appStack = CdkbootApp(
            self, 'app',
            synthesizer = cdk.DefaultStackSynthesizer(
                qualifier = '4n6ir'
            )
        )
