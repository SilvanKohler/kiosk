import random
import uuid
import datetime
from werkzeug.urls import url_parse
from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, render_template, request, jsonify, redirect, config, session
import os
import _shared.data as data
import _server.core as core
import directories
import _server.mail as mail

data.init('server')

app = Flask(__name__, template_folder=os.path.join(directories.__templates__))
app.secret_key = bytes(random.randrange(4096))
app.jinja_env.filters['zip'] = zip


def authentification(level_requirement):
    usid = session.get('usid')
    level = 0
    if usid is not None:
        user = data.User(usid=usid)
        level = user.level
    return level >= level_requirement


@app.route('/login', methods=['POST'])
def root_login():
    if request.form.get('otp'):
        session['usid'] = data.check_otp(request.form.get('otp'))
    else:
        session['usid'] = None
    return redirect(url_parse(request.referrer).path)


@app.route('/')
def root():
    if authentification(0):
        return render_template('index.html')
    else:
        return render_template('login.html')


@app.route('/settings')
def root_settings():
    if authentification(1):
        return render_template('settings.html')
    else:
        return render_template('login.html')


@app.route('/products', methods=['GET', 'POST'])
def root_management():
    if authentification(2):
        if request.args:
            changes = {}
            deletions = []
            for key, value in request.args.items():
                if key == 'select-all' or value == '':
                    pass
                elif 'select-' in key:
                    prid = key.replace('select-', '')
                    if not prid == 'new' and value == 'on':
                        deletions.append(prid)
                elif 'name-' in key:
                    prid = key.replace('name-', '')
                    if not changes.get(prid):
                        changes[prid] = {}
                    changes[prid].update({'name': value})
                elif 'stock-' in key:
                    prid = key.replace('stock-', '')
                    if not changes.get(prid):
                        changes[prid] = {}
                    try:
                        changes[prid].update({'stock': int(value)})
                    except ValueError as e:
                        break
                elif 'warning-' in key:
                    prid = key.replace('warning-', '')
                    if not changes.get(prid):
                        changes[prid] = {}
                    try:
                        changes[prid].update({'warning': int(value)})
                    except ValueError as e:
                        break
                elif 'price-' in key:
                    prid = key.replace('price-', '')
                    if not changes.get(prid):
                        changes[prid] = {}
                    try:
                        changes[prid].update({'price': float(value)})
                    except ValueError:
                        break
                    finally:
                        # Check if positive.
                        if float(value) + abs(float(value)) == 0:
                            break
            else:
                for prid, values in changes.items():
                    if prid == 'new':
                        data.create_product(
                            values['name'], values['stock'], values['warning'], values['price'])
                    else:
                        data.update_product(
                            prid, values['name'], values['stock'], values['warning'], values['price'])
                for prid in deletions:
                    data.delete_product(prid)
            return redirect('/products')
        return render_template('products.html', products=data.get_products())
    else:
        return render_template('login.html')


@app.route('/transactions', methods=['GET', 'POST'])
def root_transactions():
    if authentification(2):
        number_of_transactions = 10
        if request.args.get('number_of_transactions', None) is not None:
            try:
                number_of_transactions = int(
                    request.args['number_of_transactions'])
            except ValueError:
                pass
        return render_template('transactions.html', transactions=sorted(data.get_transactions().items(), key=lambda d: datetime.datetime.strptime(d[1]['datetime'], "%d-%m-%Y_%H:%M:%S").timestamp(), reverse=True),
                               number_of_transactions=number_of_transactions, list=list, users=data.get_users())
    else:
        return render_template('login.html')


@app.route('/purchases', methods=['GET', 'POST'])
def root_purchases():
    if authentification(2):
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
                    puid = key.replace('select-', '')
                    if value == 'on':
                        deletions.append(puid)
            else:
                for puid in deletions:
                    data.revert_purchase(puid)
            return redirect(f'/purchases?number_of_purchases={number_of_purchases}')
        return render_template('purchases.html', purchases=sorted(data.get_purchases().items(), key=lambda d: datetime.datetime.strptime(d[1]['datetime'], "%d-%m-%Y_%H:%M:%S").timestamp(), reverse=True),
                               number_of_purchases=number_of_purchases, list=list, users=data.get_users(), products=data.get_products())
    else:
        return render_template('login.html')


@app.route('/billing', methods=['GET', 'POST'])
def root_billing():
    if authentification(2):
        if request.args:
            changes = {}
            for key, value in request.args.items():
                if 'action-' in key:
                    usid = key.replace('action-', '')
                    if not changes.get(usid):
                        changes[usid] = {}
                    changes[usid].update({'action': value})
                elif 'value-' in key:
                    usid = key.replace('value-', '')
                    if not changes.get(usid):
                        changes[usid] = {}
                    try:
                        changes[usid].update({'value': float(value)})
                    except ValueError:
                        if value == '':
                            changes[usid].update({'value': float(0)})
                        else:
                            break
            else:
                for usid, values in changes.items():
                    if str(values['action']).lower() in ('twint', 'bar', 'korrektur', 'sonstig') and values['value'] != 0:
                        data.create_transaction(
                            usid, values['value'], values['action'])
            return redirect('/billing')
        users = data.get_users()
        for user in users.keys():
            transactions = data.get_transactions(user)
            purchases = data.get_purchases(user)
            users[user]['balance'] = sum(map(lambda x: x[1]['amount'], transactions.items(
            ))) - sum(map(lambda x: x[1]['amount'], purchases.items()))
        return render_template('billing.html', list=list, users=users)
    else:
        return render_template('login.html')


############### API #################


@app.route('/api/<table>/get', methods=['POST'])
def root_api_get(table):
    content = core.get(table, request.form)
    return jsonify(content), 200 if content['success'] else 406


@app.route('/api/<table>/create', methods=['POST'])
def root_api_create(table):
    content = core.create(table, request.form)
    return jsonify(content), 200 if content['success'] else 406


@app.route('/api/<table>/edit', methods=['POST'])
def root_api_edit(table):
    content = core.edit(table, request.form)
    return jsonify(content), 200 if content['success'] else 406


@app.route('/api/<table>/delete', methods=['POST'])
def root_api_delete(table):
    content = core.delete(table, request.form)
    return jsonify(content), 200 if content['success'] else 406

############## MAIL #################


def send_expense_mails():
    print('Sending Mails.')
    for user in data.get_users().items():
        print('Mail an', user[1]['email'])
        mail.send_expenses(user[0])


def send_stock_mails():
    for product in data.get_products().items():
        if product[1]['stock'] <= product[1]['warning']:
            mail.send_stock(product[1])


if __name__ == "__main__":
    sched = BackgroundScheduler()
    sched.add_job(send_expense_mails, 'interval', days=30)
    sched.add_job(send_stock_mails, 'interval', days=7)
    sched.start()
    app.run("0.0.0.0", 80)
