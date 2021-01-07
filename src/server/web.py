from flask import Flask, redirect, session, render_template
import random

app = Flask(__name__)
app.secret_key = bytes(random.randrange(4096))

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/settings')
def root_settings():
    return render_template('settings.html')

@app.route('/management')
def root_management():
    return render_template('management.html')
