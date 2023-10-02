FROM public.ecr.aws/forensicir/getpublicip:latest AS layer
FROM public.ecr.aws/lambda/python:latest
RUN yum -y update && yum clean all
### layer code ###
WORKDIR /opt
COPY --from=layer /opt/ .
### function code ###
WORKDIR /var/task
COPY version.py /var/task/version.py
COPY requirements.txt /var/task/requirements.txt
RUN pip --no-cache-dir install -r requirements.txt --upgrade
CMD ["version.handler"]