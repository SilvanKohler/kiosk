#!/usr/bin/python3
from wsgiref.handlers import CGIHandler
from kiosk import app

CGIHandler().run(app)