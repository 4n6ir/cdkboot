# CDK v2.99.1
FROM public.ecr.aws/forensicir/getpublicip:latest AS layer
FROM public.ecr.aws/lambda/python:latest
RUN yum -y update
RUN yum install https://rpm.nodesource.com/pub_20.x/nodistro/repo/nodesource-release-nodistro-1.noarch.rpm -y
RUN yum install nsolid -y
RUN npm install -g aws-cdk@latest
RUN yum clean all
### layer code ###
WORKDIR /opt
COPY --from=layer /opt/ .
### function code ###
WORKDIR /var/task
COPY install.py /var/task/install.py
COPY requirements.txt /var/task/requirements.txt
RUN pip --no-cache-dir install -r requirements.txt --upgrade
CMD ["install.handler"]