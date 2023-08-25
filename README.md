# cdkboot

CDKBOOT keeps the bootstrap version current with the latest release to support continuous deployments!

The GitHub repository RSS feed gets monitored for CDK v2 releases.

https://github.com/aws/aws-cdk/releases.atom

The latest Cloud Development Kit (CDK) release generates and uploads the Cloud Formation bootstrap to an S3 bucket.

```
export CDK_NEW_BOOTSTRAP=1 && cdk bootstrap --show-template > /tmp/cdk.yaml
```

CDK bootstrap is manually deployed using Organization StackSets from a delegated administrator account with names beginning with ```cdk-bootstrap-4n6ir-``` where ```4n6ir``` changes for the specific qualifier.

This provides a method to identify which stacks need updates when the bootstrap changes.

https://docs.aws.amazon.com/cdk/latest/guide/bootstrapping.html#bootstrapping-contract

Organization StackSets are unavailable in the **management (root) account** or newly launched regions.

- Israel (Tel Aviv) **il-central-1**

The bootstrap template created by CDKBOOT can deploy a regular Cloud Formation Stack if necessary for these locations with the existing S3 permissions.
