FROM python:3.9
MAINTAINER Silvan Kohler "silvankohler@protonmail.com"
WORKDIR /kiosk
RUN python3 -m pip install --no-cache-dir uwsgi
        
COPY serverrequirements.txt serverrequirements.txt
RUN python3 -m pip install --no-cache-dir -r serverrequirements.txt
RUN export PYTHON=python3.8

RUN useradd -ms /bin/bash uwsgi

COPY src src
RUN chmod -R 777 src
WORKDIR /kiosk/src
CMD [ "uwsgi", "--http", "0.0.0.0:80", \
               "--uid", "uwsgi", \
               "--plugins", "python3", \
               "--protocol", "uwsgi", \
               "--wsgi-file", "server.py", \
               "--enable-threads" ]