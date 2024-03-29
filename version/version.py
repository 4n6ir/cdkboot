import boto3
import feedparser
import json
import os
from github import Github

def handler(event, context):

    try:
        poll_response = feedparser.parse('https://github.com/aws/aws-cdk/releases.atom')
    except:
        raise ValueError('RSS/Atom Feed Failure')  

    ssm_client = boto3.client('ssm')
    
    response = ssm_client.get_parameter(
        Name = os.environ['VERSIONS']
    )
    
    prevtoken = response['Parameter']['Value']

    if poll_response.entries[0].title != prevtoken:

        if poll_response.entries[0].title[0:2] == 'v2':

            f = open('/tmp/Dockerfile', 'w')
            f.write('# CDK '+poll_response.entries[0].title+'\n')
            f.write('FROM public.ecr.aws/forensicir/getpublicip:latest AS layer\n')
            f.write('FROM public.ecr.aws/lambda/python:latest\n')
            f.write('RUN yum -y update\n')
            f.write('RUN yum install https://rpm.nodesource.com/pub_16.x/nodistro/repo/nodesource-release-nodistro-1.noarch.rpm -y\n')
            f.write('RUN yum install nodejs -y --setopt=nodesource-nodejs.module_hotfixes=1\n')
            f.write('RUN npm install -g aws-cdk@latest\n')
            f.write('RUN yum clean all\n')
            f.write('### layer code ###\n')
            f.write('WORKDIR /opt\n')
            f.write('COPY --from=layer /opt/ .\n')
            f.write('### function code ###\n')
            f.write('WORKDIR /var/task\n')
            f.write('COPY install.py /var/task/install.py\n')
            f.write('COPY requirements.txt /var/task/requirements.txt\n')
            f.write('RUN pip --no-cache-dir install -r requirements.txt --upgrade\n')
            f.write('CMD ["install.handler"]')
            f.close()

            with open('/tmp/Dockerfile', 'r') as f:
                data = f.read()
            f.close()

            secret_client = boto3.client('secretsmanager')

            response = secret_client.get_secret_value(
                SecretId = 'github-token'
            )

            g = Github(response['SecretString'])

            repo = g.get_repo('jblukach/cdkboot')

            contents = repo.get_contents('install/Dockerfile')

            repo.update_file(contents.path, poll_response.entries[0].title, data, contents.sha)

            response = ssm_client.put_parameter(
                Name = os.environ['VERSIONS'],
                Value = poll_response.entries[0].title,
                Type = 'String',
                Overwrite = True
            )

    return {
        'statusCode': 200,
        'body': json.dumps('CDKBoot Version')
    }