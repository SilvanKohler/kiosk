from flask import Flask, redirect, session, render_template, request, jsonify
from flask_restful import Resource, Api
import random
import uuid
from time import sleep
from threading import Thread

from tables import chain, results, run

app = Flask(__name__)
app.secret_key = bytes(random.randrange(4096))
app.jinja_env.filters['zip'] = zip
api = Api(app)

get_transactions = None
get_drinks = None
update_drink = None


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/settings')
def root_settings():
    return render_template('settings.html')


@app.route('/management', methods=['GET', 'POST'])
def root_management():
    print(request.args)
    if request.args:
        changes = {}
        for key, value in request.args.items():
            if key == 'select-all':
                pass
            elif 'select-' in key:
                did = key.replace('select-', '')
            elif 'name-' in key:
                did = key.replace('name-', '')
                if not changes.get(did):
                    changes[did] = {}
                changes[did].update({'name': value})
            elif 'lager-' in key:
                did = key.replace('lager-', '')
                if not changes.get(did):
                    changes[did] = {}
                changes[did].update({'lager': int(value)})
            elif 'preis-' in key:
                did = key.replace('preis-', '')
                if not changes.get(did):
                    changes[did] = {}
                changes[did].update({'preis': int(value)})
        for did, values in changes.items():
            update_drink(did, values['name'], values['lager'], values['preis'], )
    return render_template('management.html', drinks=get_drinks(), new_uuid=uuid.uuid1().hex)


@app.route('/transactions', methods=['GET', 'POST'])
def root_transactions():
    number_of_transactions = 10
    if request.form:
        number_of_transactions = request.form['number_of_transactions']
    return render_template('transactions.html', transactions=get_transactions(),
                           number_of_transactions=number_of_transactions)


@app.route('/billing')
def root_billing():
    return render_template('billing.html')


############### API #################
@app.route('/api/customer/<uid>', methods=['GET'])
def root_api_customer_uid(uid):
    content = {'success': False}
    i = uuid.uuid1().hex
    chain.put(['get', 'customer', i])
    while results.get(i) is None:
        sleep(0.05)
    print(dict(results.get(i)).items())
    for UID, (firstname, lastname, email, balance, avatar) in dict(results.get(i)).items():
        if UID == uid or uid == '0':
            content.update({
                'success': True,
                UID: {
                    'firstname': firstname,
                    'lastname': lastname,
                    'email': email,
                    'balance': balance,
                    'avatar': avatar
                }
            })
    return jsonify(content), 200 if content['success'] else 406
@app.route('/api/customer', methods=['POST'])
def root_api_customer():
    content = {'success': False}
    try:
        uid = uuid.uuid1().hex
        attributes = request.form
        chain.put(['update', 'customer', {
            uid: (attributes['firstname'].upper(), attributes['lastname'].upper(), attributes['email'].upper(), attributes['balance'], attributes['avatar'])
        }])
    finally:
        content['success'] = True
    return jsonify(content), 200 if content['success'] else 406
Thread(target=run).start()
app.run("0.0.0.0", 80, debug=True)
