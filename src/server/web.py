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
    'user': ('uid', ('firstname', 'lastname', 'email', 'balance', 'avatar')),
    'badge': ('bid', ('badgenumber', 'uid')),
    'drink': ('did', ('name', 'stock', 'price')),
    'purchase': ('pid', ('datetime', 'did', 'uid', 'amount')),
    'transaction': ('tid', ('datetime', 'uid', 'amount')),
    'mail': ('mid', ('datetime', 'uid', 'balance'))
}


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/settings')
def root_settings():
    return render_template('settings.html')


@app.route('/drinks', methods=['GET', 'POST'])
def root_management():
    print(request.args)
    if request.args:
        changes = {}
        deletions = []
        for key, value in request.args.items():
            print(key, value)
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
                    print('stock======================================================', key, value)
                    break
            elif 'price-' in key:
                did = key.replace('price-', '')
                if not changes.get(did):
                    changes[did] = {}
                try:
                    changes[did].update({'price': float(value)})
                except ValueError:
                    print('price======================================================')
                    break
                finally:
                    if float(value) + abs(float(value)) == 0: # Check if positive.
                        print('priceprice======================================================')
                        break
        else:
            for did, values in changes.items():
                if did == 'new':
                    data.create_drink(values['name'], values['stock'], values['price'])
                else:
                    data.update_drink(did, values['name'], values['stock'], values['price'])
            print(changes)
            print(deletions)
            for did in deletions:
                data.delete_drink(did)
        return redirect('/drinks')
    return render_template('drinks.html', drinks=data.get_drinks())


@app.route('/transactions', methods=['GET', 'POST'])
def root_transactions():
    number_of_transactions = 10
    if request.form:
        number_of_transactions = request.form['number_of_transactions']
    return render_template('transactions.html', transactions=data.get_transactions(),
                           number_of_transactions=number_of_transactions)

@app.route('/purchases', methods=['GET', 'POST'])
def root_purchases():
    if request.args.get('number_of_purchases', None) is not None:
        try:
            number_of_purchases = int(request.args['number_of_purchases'])
        except ValueError:
            number_of_purchases = 10
    else:
        number_of_purchases = 10
    return render_template('purchases.html', purchases=sorted(data.get_purchases().items(), key=lambda d: datetime.datetime.strptime(d[1]['datetime'], "%d-%m-%Y_%H:%M:%S").timestamp(), reverse=True),
                           number_of_purchases=number_of_purchases, list=list, users=data.get_users(), drinks=data.get_drinks())

@app.route('/billing')
def root_billing():
    return render_template('billing.html')


############### API #################

@app.route('/api/<table>/get', methods=['POST'])
def root_api_get(table):
    content = {'success': False}
    if table in tables.tables.keys():
        parameters = {
            key: (float(value) if key in ['balance', 'amount', 'price'] else int(value) if key == 'stock' else value) for
            key, value in request.form.items()
        }
        i = uuid.uuid1().hex
        tables.chain.put(['get', table, i])
        while tables.results.get(i) is None:
            sleep(0.05)
        print(parameters)
        for entry in dict(tables.results.get(i)).items():
            try:
                for parameter in parameters.items():
                    print(parameter, specs[table], str(entry))
                    if parameter[0] == specs[table][0] and not str(parameter[1]) == str(entry[0]) and not str(
                            parameter[1]) == str(entry[1][parameter[0]]):
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
            key: (float(value) if key in ['balance', 'amount', 'price'] else int(value) if key == 'stock' else value) for
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
            key: (float(value) if key in ['balance', 'amount', 'price'] else int(value) if key == 'stock' else value) for
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
                tuple(parameters.items())[:pos] + tuple(parameters.items())[pos + 1:]
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
            key: (float(value) if key in ['balance', 'amount', 'price'] else int(value) if key == 'stock' else value) for
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
