from flask import Flask, redirect, session
import random
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
auth = HTTPBasicAuth()
app.secret_key = bytes(random.randrange(4096))
users = {
    "test": generate_password_hash("12345678"),
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/')
@auth.login_required
def root():
    return auth.username()

@app.route('/logout')
def root_logout():
    return "logged out", 401


app.run("0.0.0.0", 80, debug=True)
