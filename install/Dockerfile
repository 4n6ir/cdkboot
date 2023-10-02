# CDK v2.99.1
FROM public.ecr.aws/forensicir/getpublicip:latest AS layer
FROM public.ecr.aws/lambda/python:latest
RUN yum -y update
RUN curl -sL https://rpm.nodesource.com/setup_18.x | bash -
RUN yum list available nodejs
RUN yum install -y nodejs
RUN npm install -g aws-cdk@latest
RUN yum clean all
### layer code ###
WORKDIR /opt
COPY --from=layer /opt/ .
### function code ###
WORKDIR /var/task
COPY install.py requirements.txt /var/task/ .
RUN pip --no-cache-dir install -r requirements.txt --upgrade
CMD ["install.handler"]