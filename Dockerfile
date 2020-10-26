FROM python:3.6-slim

RUN apt-get -y update
RUN apt-get install -y build-essential
RUN apt-get -y install curl
RUN apt-get install -y vim
RUN apt-get install -y nano

ADD . /opt/
WORKDIR /opt/
RUN rm -rf .git
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "./app.py"]