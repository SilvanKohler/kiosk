#!/bin/bash
cd ~/kiosk
source linuxvenv/bin/activate
cd src
export DISPLAY=:1
python3 client.py
