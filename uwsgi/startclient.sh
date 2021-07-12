#!/bin/bash
cd /home/pi/kiosk/uwsgi
export DISPLAY=:1
python3 client.py &