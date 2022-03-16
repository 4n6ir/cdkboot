FROM public.ecr.aws/lambda/python:latest
RUN yum update -y
RUN pip install feedparser PyGithub
COPY version.py ./
CMD ["version.handler"]