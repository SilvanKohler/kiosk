import random
import re
import uuid
from threading import Thread
from time import sleep
import datetime

from flask import Flask, render_template, request, jsonify, redirect

import shared.data as data
import server.tables as tables

app = Flask(__name__)
app.secret_key = bytes(random.randrange(4096))
app.jinja_env.filters['zip'] = zip

specs = {
    'user': ('uid', ('firstname', 'lastname', 'email', 'avatar')),
    'badge': ('bid', ('badgenumber', 'uid')),
    'drink': ('did', ('name', 'stock', 'price')),
    'purchase': ('pid', ('datetime', 'did', 'uid', 'amount')),
    'transaction': ('tid', ('datetime', 'uid', 'amount', 'reason')),
    'mail': ('mid', ('datetime', 'uid', 'balance'))
}
floats = ['amount', 'price']
ints = ['stock', 'badgenumber']


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/settings')
def root_settings():
    return render_template('settings.html')


@app.route('/drinks', methods=['GET', 'POST'])
def root_management():
    if request.args:
        changes = {}
        deletions = []
        for key, value in request.args.items():
            if key == 'select-all' or value == '':
                pass
            elif 'select-' in key:
                did = key.replace('select-', '')
                if not did == 'new' and value == 'on':
                    deletions.append(did)
            elif 'name-' in key:
                did = key.replace('name-', '')
                if not changes.get(did):
                    changes[did] = {}
                changes[did].update({'name': value})
            elif 'stock-' in key:
                did = key.replace('stock-', '')
                if not changes.get(did):
                    changes[did] = {}
                try:
                    changes[did].update({'stock': int(value)})
                except ValueError as e:
                    break
            elif 'price-' in key:
                did = key.replace('price-', '')
                if not changes.get(did):
                    changes[did] = {}
                try:
                    changes[did].update({'price': float(value)})
                except ValueError:
                    break
                finally:
                    # Check if positive.
                    if float(value) + abs(float(value)) == 0:
                        break
        else:
            for did, values in changes.items():
                if did == 'new':
                    data.create_drink(
                        values['name'], values['stock'], values['price'])
                else:
                    data.update_drink(
                        did, values['name'], values['stock'], values['price'])
            for did in deletions:
                data.delete_drink(did)
        return redirect('/drinks')
    return render_template('drinks.html', drinks=data.get_drinks())


@app.route('/transactions', methods=['GET', 'POST'])
def root_transactions():
    number_of_transactions = 10
    if request.args.get('number_of_transactions', None) is not None:
        try:
            number_of_transactions = int(
                request.args['number_of_transactions'])
        except ValueError:
            pass
    return render_template('transactions.html', transactions=sorted(data.get_transactions().items(), key=lambda d: datetime.datetime.strptime(d[1]['datetime'], "%d-%m-%Y_%H:%M:%S").timestamp(), reverse=True),
                           number_of_transactions=number_of_transactions, list=list, users=data.get_users())


@app.route('/purchases', methods=['GET', 'POST'])
def root_purchases():
    number_of_purchases = 10
    if request.args.get('number_of_purchases', None) is not None:
        try:
            number_of_purchases = int(request.args['number_of_purchases'])
        except ValueError:
            pass
    if any('select' in key for key in list(request.args.keys())):
        deletions = []
        for key, value in request.args.items():
            if 'select-' in key:
                pid = key.replace('select-', '')
                if value == 'on':
                    deletions.append(pid)
        else:
            for pid in deletions:
                data.revert_purchase(pid)
        return redirect(f'/purchases?number_of_purchases={number_of_purchases}')
    return render_template('purchases.html', purchases=sorted(data.get_purchases().items(), key=lambda d: datetime.datetime.strptime(d[1]['datetime'], "%d-%m-%Y_%H:%M:%S").timestamp(), reverse=True),
                           number_of_purchases=number_of_purchases, list=list, users=data.get_users(), drinks=data.get_drinks())


@app.route('/billing', methods=['GET', 'POST'])
def root_billing():
    if request.args:
        changes = {}
        print(list(request.args.items()))
        for key, value in request.args.items():
            if 'action-' in key:
                uid = key.replace('action-', '')
                if not changes.get(uid):
                    changes[uid] = {}
                changes[uid].update({'action': value})
            elif 'value-' in key:
                uid = key.replace('value-', '')
                if not changes.get(uid):
                    changes[uid] = {}
                try:
                    changes[uid].update({'value': float(value)})
                except ValueError:
                    if value == '':
                        changes[uid].update({'value': float(0)})
                    else:
                        break
        else:
            for uid, values in changes.items():
                if str(values['action']).lower() in ('twint', 'bar', 'korrektur', 'sonstig') and values['value'] != 0:
                    data.create_transaction(
                        uid, values['value'], values['action'])
        return redirect('/billing')
    users = data.get_users()
    for user in users.keys():
        transactions = data.get_transactions(user)
        purchases = data.get_purchases(user)
        users[user]['balance'] = sum(map(lambda x: x[1]['amount'], transactions.items(
        ))) - sum(map(lambda x: x[1]['amount'], purchases.items()))
    return render_template('billing.html', list=list, users=users)

############### API #################


@app.route('/api/<table>/get', methods=['POST'])
def root_api_get(table):
    content = {'success': False}
    if table in tables.tables.keys():
        parameters = {
            key: (float(value) if key in floats else int(value) if key in ints else value) for
            key, value in request.form.items()
        }
        i = uuid.uuid1().hex
        tables.chain.put(['get', table, i])
        while tables.results.get(i) is None:
            sleep(0.05)
        for entry in dict(tables.results.get(i)).items():
            try:
                for parameter in parameters.items():
                    if not ((parameter[0] == specs[table][0] and str(parameter[1]).lower() == str(entry[0]).lower()) or (parameter[0] in specs[table][1] and str(
                            parameter[1]).lower() == str(entry[1][parameter[0]]).lower())):
                        break
                else:
                    content.update({
                        entry[0]: {
                            key: value for key, value in entry[1].items()
                        }
                    })
                    content['success'] = True
            except (KeyError, re.error):
                pass
    return jsonify(content), 200 if content['success'] else 406


@app.route('/api/<table>/create', methods=['POST'])
def root_api_create(table):
    content = {'success': False}
    if table in tables.tables.keys():
        parameters = {
            key: (float(value) if key in floats else int(value) if key in ints else value) for
            key, value in request.form.items()
        }
        try:
            i = uuid.uuid1().hex
            tables.chain.put(['update', table, {
                i: {
                    spec: parameters[spec] for spec in specs[table][1]
                }
            }])
            content[specs[table][0]] = i
            content['success'] = True
        except KeyError:
            pass
    return jsonify(content), 200 if content['success'] else 406


@app.route('/api/<table>/edit', methods=['POST'])
def root_api_edit(table):
    content = {'success': False}
    if table in tables.tables.keys():
        parameters = {
            key: (float(value) if key in floats else int(value) if key in ints else value) for
            key, value in request.form.items()
        }
        try:
            pos = tuple(parameters.keys()).index(specs[table][0])
            i = uuid.uuid1().hex
            tables.chain.put(['get', table, i])
            while tables.results.get(i) is None:
                sleep(0.05)
            d = tables.results.get(i)
            d[parameters[specs[table][0]]].update({
                parameter[0]: parameter[1] for parameter in
                tuple(parameters.items())[:pos] +
                tuple(parameters.items())[pos + 1:]
            })
            tables.chain.put(['update', table, d])
            content['success'] = True
        except KeyError:
            pass
    return jsonify(content), 200 if content['success'] else 406


@app.route('/api/<table>/delete', methods=['POST'])
def root_api_delete(table):
    content = {'success': False}
    if table in tables.tables.keys():
        parameters = {
            key: (float(value) if key in floats else int(value) if key in ints else value) for
            key, value in request.form.items()
        }
        try:
            i = uuid.uuid1().hex
            tables.chain.put(['del', table, parameters[specs[table][0]]])
            content['success'] = True
        except:
            pass
    return jsonify(content), 200 if content['success'] else 406

if __name__ == "__main__":
    Thread(target=tables.run).start()
    app.run("0.0.0.0", 80, debug=True)
