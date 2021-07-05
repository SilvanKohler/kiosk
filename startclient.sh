#!/bin/bash
cd /home/pi/kiosk/src
export DISPLAY=:1
python3 client.py &
echo $$ > /home/pi/kiosk/kiosk.pid
type /home/pi/kiosk/kiosk.pid