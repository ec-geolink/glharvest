FROM python:2.7.10
MAINTAINER Bryce Mecum <brycemecum@gmail.com>

RUN apt-get update && apt-get install -y python-librdf

WORKDIR /usr/local/worker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY start.sh start.sh
COPY work.py work.py

CMD [ "sh", "start.sh" ]
