import os, sys, random

# edit your username below
sys.path.append("/home/username/public_html/kiosk/src")

sys.path.insert(0, os.path.dirname(__file__))
from server import app as application

# make the secret code a little better
application.secret_key = bytes(random.randrange(4096))