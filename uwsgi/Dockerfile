FROM python:3.9
RUN python3 -m pip install --no-cache-dir uwsgi
        
COPY . /kiosk
WORKDIR /kiosk

RUN python3 -m pip install --no-cache-dir -r serverrequirements.txt
RUN export PYTHON=python3.8

RUN useradd -ms /bin/bash uwsgi

RUN chown -R uwsgi:uwsgi *
RUN mkdir data backup
RUN chmod -R 777 data backup
CMD [ "uwsgi", "uwsgi.ini", "--uid", "uwsgi", "--gid", "uwsgi"]