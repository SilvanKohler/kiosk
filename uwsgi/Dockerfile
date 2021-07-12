FROM rust AS python3-cryptography
RUN apt update
RUN apt install -y python3 python3-pip
WORKDIR /wheels
RUN python3 -m pip wheel cryptography

FROM python:3.9

COPY . /kiosk
WORKDIR /kiosk

COPY --from=python3-cryptography /wheels /wheels
RUN python3 -m pip install /wheels/*


RUN apt install python3-gdbm
RUN python3 -m pip install uwsgi
RUN python3 -m pip install $(cat serverrequirements.txt) 
RUN export PYTHON=python3

RUN useradd -ms /bin/bash uwsgi

RUN chown -R uwsgi:uwsgi *
RUN mkdir data backup
RUN chmod -R 777 data backup
CMD [ "uwsgi", "uwsgi.ini", "--uid", "uwsgi", "--gid", "uwsgi"]