# CDK v2.110.0
FROM public.ecr.aws/forensicir/getpublicip:latest AS layer
FROM public.ecr.aws/provided.al2023
RUN dnf -y update
RUN dnf install -y python3
RUN dnf module list nodejs
RUN dnf module install nodejs -y
RUN npm install -g aws-cdk@latest
RUN dnf clean all
### layer code ###
WORKDIR /opt
COPY --from=layer /opt/ .
### function code ###
WORKDIR /var/task
COPY install.py /var/task/install.py
COPY requirements.txt /var/task/requirements.txt
RUN pip --no-cache-dir install -r requirements.txt --upgrade
CMD ["install.handler"]