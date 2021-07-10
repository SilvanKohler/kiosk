FROM rust
RUN apt update
RUN apt install -y python3 python3-pip python3-gdbm

RUN python3 -m pip install uwsgi

COPY . /kiosk
WORKDIR /kiosk

RUN python3 -m pip install -r serverrequirements.txt
RUN export PYTHON=python3.8

RUN useradd -ms /bin/bash uwsgi

RUN chown -R uwsgi:uwsgi *
RUN mkdir data backup
RUN chmod -R 777 data backup
CMD [ "uwsgi", "uwsgi.ini", "--uid", "uwsgi", "--gid", "uwsgi"]