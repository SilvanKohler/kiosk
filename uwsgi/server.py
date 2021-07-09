import random
import datetime
from werkzeug.urls import url_parse
from flask_apscheduler import APScheduler
import shutil
from flask import Flask, render_template, request, jsonify, redirect, config, session, g
import os
import _shared.data as data
import _server.core as core
import _server.mail as mail
import configparser
import requests

data.init('server')

cparser = configparser.ConfigParser()
cparser.read(['default_config.ini', 'config.ini'])

app = Flask(__name__, template_folder=os.path.abspath(cparser.get('directories', 'templates')))
app.secret_key = bytes(random.randrange(4096))
app.jinja_env.filters['zip'] = zip


@app.before_request
def before_request():
    usid = session.get('usid')
    g.level = 0
    if usid is not None:
        user = data.User(usid=usid)
        g.level = user.level
    


@app.route('/login', methods=['GET', 'POST'])
def root_login():
    if request.method == 'GET':
        return render_template('login.html', level=g.level)
    else:
        if request.form.get('otp'):
            session['usid'] = data.check_otp(request.form.get('otp'))
        else:
            session['usid'] = None
        return redirect(url_parse(request.referrer).path if url_parse(request.referrer).path != '/login' else '/')


@app.route('/')
def root():
    if g.level >= 0:
        releases = requests.get('https://api.github.com/repos/SilvanKohler/kiosk/releases').json()
        return render_template('index.html', level=g.level, releases=sorted(releases, key=lambda d: d['tag_name'], reverse=True), enumerate=enumerate)
    else:
        return render_template('login.html', level=g.level)


@app.route('/settings')
def root_settings():
    if g.level >= 1:
        return render_template('settings.html', level=g.level)
    else:
        return render_template('login.html', level=g.level)


@app.route('/products', methods=['GET', 'POST'])
def root_management():
    if g.level >= 2:
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
        return render_template('products.html', level=g.level, products=data.get_products())
    else:
        return render_template('login.html', level=g.level)


@app.route('/transactions', methods=['GET', 'POST'])
def root_transactions():
    if g.level >= 2:
        number_of_transactions = 10
        if request.args.get('number_of_transactions', None) is not None:
            try:
                number_of_transactions = int(
                    request.args['number_of_transactions'])
            except ValueError:
                pass
        return render_template('transactions.html', level=g.level, transactions=sorted(data.get_transactions().items(), key=lambda d: datetime.datetime.strptime(d[1]['datetime'], "%d-%m-%Y_%H:%M:%S").timestamp(), reverse=True),
                               number_of_transactions=number_of_transactions, list=list, users=data.get_users())
    else:
        return render_template('login.html', level=g.level)


@app.route('/purchases', methods=['GET', 'POST'])
def root_purchases():
    if g.level >= 2:
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
        return render_template('purchases.html', level=g.level, purchases=sorted(data.get_purchases().items(), key=lambda d: datetime.datetime.strptime(d[1]['datetime'], "%d-%m-%Y_%H:%M:%S").timestamp(), reverse=True),
                               number_of_purchases=number_of_purchases, list=list, users=data.get_users(), products=data.get_products())
    else:
        return render_template('login.html', level=g.level)


@app.route('/billing', methods=['GET', 'POST'])
def root_billing():
    if g.level >= 2:
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
                elif 'level-' in key:
                    usid = key.replace('level-', '')
                    if not changes.get(usid):
                        changes[usid] = {}
                    try:
                        changes[usid].update({'level': int(value)})
                    except ValueError:
                        if value == '':
                            changes[usid].update({'level': int(0)})
                        else:
                            break
            else:
                for usid, values in changes.items():
                    if values.get('action') and values.get('value'):
                        if str(values['action']).lower() in ('twint', 'bar', 'korrektur', 'sonstig') and values['value'] != 0:
                            data.create_transaction(
                                usid, values['value'], values['action'])
                    if values.get('level'):
                        data.authorize_user(usid, values['level'])
            return redirect('/billing')
        users = data.get_users()
        for user in users.keys():
            transactions = data.get_transactions(user)
            purchases = data.get_purchases(user)
            users[user]['balance'] = sum(map(lambda x: x[1]['amount'], transactions.items(
            ))) - sum(map(lambda x: x[1]['amount'], purchases.items()))
        return render_template('billing.html', level=g.level, list=list, users=users)
    else:
        return render_template('login.html', level=g.level)


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

############## TASK ################

sched = APScheduler()

@sched.task('cron', id='send_expense_mails', day=1)
def send_expense_mails():
    print('Sending Mails.')
    for user in data.get_users().items():
        print('Mail an', user[1]['email'])
        mail.send_expenses(user[0])


@sched.task('cron', id='send_stock_mails', day_of_week=5)
def send_stock_mails():
    for product in data.get_products().items():
        if product[1]['stock'] <= product[1]['warning']:
            print(product[1]['name'])
            mail.send_stock(product[1])

@sched.task('cron', id='backup_data', hour='*/12')
def backup_data():
    data_directory = os.path.abspath(cparser.get('directories', 'data'))
    date = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    if not os.path.exists(os.path.abspath(cparser.get('directories', 'backup'))):
        os.mkdir(os.path.abspath(cparser.get('directories', 'backup')))
    backup_directory = os.path.join(os.path.abspath(cparser.get('directories', 'backup')), 'backup_data_'+date)
    print('creating backup:', backup_directory)
    for backup in os.listdir(os.path.abspath(cparser.get('directories', 'backup')))[:-cparser.getint('server', 'max_backups')]:
        os.remove(os.path.join(os.path.abspath(cparser.get('directories', 'backup')), backup))
    shutil.copytree(data_directory, backup_directory)
    shutil.make_archive(backup_directory, 'zip', backup_directory)
    shutil.rmtree(backup_directory)


sched.init_app(app)
sched.start()

if __name__ == "__main__":
    app.run("0.0.0.0", 80)
