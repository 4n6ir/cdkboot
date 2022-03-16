# cdkboot

CDKBOOT keeps the bootstrap version current with the latest release to support continuous deployments!

Accounts must be bootstrapped by CDK as the established deploy and execute role permissions update the current stack. 

I use AQUEDUCT, a CDK command line interface script, to get started quickly for organizations using single sign-on configurations.

 - https://github.com/4n6ir/aqueduct

The GitHub repository RSS feed gets monitored for CDK v2 releases. 

 - https://github.com/aws/aws-cdk/releases.atom

The Cloud Formation gets pushed out to all accounts and configured regions.

 - https://github.com/jblukach/cdkboot/blob/main/cdkboot/cdkboot_stack.py#L22

Additional information for changes to the CDK bootstrap is available to read.

 - https://docs.aws.amazon.com/cdk/latest/guide/bootstrapping.html#bootstrapping-contract