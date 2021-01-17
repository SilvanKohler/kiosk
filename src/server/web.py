from flask import Flask, redirect, session, render_template, request
import random
import uuid

app = Flask(__name__)
app.secret_key = bytes(random.randrange(4096))
app.jinja_env.filters['zip'] = zip

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
            update_drink(did, values['name'], values['lager'], values['preis'],)
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