FROM python:3.9

RUN apt update
RUN apt install -y python3 python3-pip python3-gdbm python3-cryptography=3.4.7

RUN python3 -m pip install uwsgi

COPY . /kiosk
WORKDIR /kiosk

RUN python3 -m pip install $(cat serverrequirements.txt) 
RUN export PYTHON=python3.9

RUN useradd -ms /bin/bash uwsgi

RUN chown -R uwsgi:uwsgi *
RUN mkdir data backup
RUN chmod -R 777 data backup
CMD [ "uwsgi", "uwsgi.ini", "--uid", "uwsgi", "--gid", "uwsgi"]