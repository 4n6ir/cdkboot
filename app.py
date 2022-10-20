#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdkboot.cdkboot_stack import CdkbootStack

app = cdk.App()

CdkbootStack(
    app, 'CdkbootStack',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = os.getenv('CDK_DEFAULT_REGION')
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

cdk.Tags.of(app).add('Alias','Pipeline')
cdk.Tags.of(app).add('GitHub','https://github.com/jblukach/cdkboot.git')

app.synth()
