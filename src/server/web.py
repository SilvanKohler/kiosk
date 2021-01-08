from flask import Flask, redirect, session, render_template, request
import random

app = Flask(__name__)
app.secret_key = bytes(random.randrange(4096))
get_transactions = None


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/settings')
def root_settings():
    return render_template('settings.html')


@app.route('/management', methods=['GET', 'POST'])
def root_management():
    if request.form:
        print(request.form)
    return render_template('management.html')


@app.route('/transactions', methods=['GET', 'POST'])
def root_transactions():
    number_of_transactions = 10
    if request.form:
        number_of_transactions = request.form['number_of_transactions']
    return render_template('transactions.html', transactions=get_transactions(),
                           number_of_transactions=number_of_transactions)
