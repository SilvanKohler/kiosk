import datetime
import os
from shared.api import API

default_avatar = 'https://murwillumbahvet.com.au/wp-content/uploads/2019/08/profile-blank.png'

# default_avatar = 'https://media.giphy.com/media/QuPrp3BI6cMe2lErCb/giphy.gif'
if os.name == 'nt':
    host = '127.0.0.1'
else:
    host = '192.168.137.1'
port = 80
protocol = 'http'
api = API(host, port, protocol)


class User:
    def __init__(self, badgenumber=None, firstname=None, lastname=None, email=None, uid=None):
        if firstname is not None:
            self.firstname = firstname
            self.lastname = lastname
            self.email = email
            self.badges = [badgenumber]
            self.register()
        if uid is not None:
            self.uid = uid
        else:
            self.badges = [badgenumber]
            self.uid = self.get_uid()
        self.firstname = self.get_firstname()
        self.lastname = self.get_lastname()
        self.email = self.get_email()
        self.balance = self.get_balance()
        self.badges = self.get_badges()

    def register(self):
        uid = api.create('user', {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'balance': 0.0,
            'avatar': default_avatar
        })['uid']
        api.create('badge', {
            'badgenumber': self.badges[0],
            'uid': uid
        })

    def get_firstname(self):
        return api.get('user', {
            'uid': self.uid
        })[self.uid]['firstname']

    def get_lastname(self):
        return api.get('user', {
            'uid': self.uid
        })[self.uid]['lastname']

    def get_email(self):
        return api.get('user', {
            'uid': self.uid
        })[self.uid]['email']

    def get_balance(self):
        return api.get('user', {
            'uid': self.uid
        })[self.uid]['balance']

    def get_avatar(self):
        return api.get('user', {
            'uid': self.uid
        })[self.uid]['avatar']

    def get_badges(self):
        badges = api.get('badge', {
            'uid': self.uid
        })
        return [x['badgenumber'] for x in dict(filter(lambda x: x[0] != 'success', badges.items())).values()]

    def get_uid(self):
        badges = api.get('badge', {
            'badgenumber': self.badges[0]
        })
        return list(dict(filter(lambda x: x[0] != 'success', dict(badges).items())).values())[0]['uid']

    def get_purchases(self):
        purchases = api.get('purchase', {
            'uid': self.uid
        })
        return dict(filter(lambda x: x[0] != 'success', purchases.items()))

    def get_transactions(self):
        transactions = api.get('transaction', {
            'uid': self.uid
        })
        return dict(filter(lambda x: x[0] != 'success', transactions.items()))

    def buy(self, did):
        drink = get_drink(did)[did]
        price = drink['price']
        api.edit('user', {'uid': self.uid}, {
            'balance': self.get_balance() - price
        })
        date = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        api.create('purchase', {
            'datetime': date,
            'did': did,
            'uid': self.uid,
            'amount': price
        })


def register_user(firstname, lastname, email, badgenumber):
    user = User(firstname=firstname, lastname=lastname,
                email=email, badgenumber=badgenumber)
    return user


def login_user(badgenumber):
    user = User(badgenumber=badgenumber)
    return user


def get_transactions():
    transactions = api.get('transaction', {})
    return dict(filter(lambda x: x[0] != 'success', transactions.items()))


def get_purchases():
    purchases = api.get('purchase', {})
    return dict(filter(lambda x: x[0] != 'success', purchases.items()))


def get_users():
    users = api.get('user', {})
    return dict(filter(lambda x: x[0] != 'success', users.items()))


def get_badges():
    badges = api.get('badge', {})
    return dict(filter(lambda x: x[0] != 'success', badges.items()))


def get_drinks():
    drinks = api.get('drink', {})
    return dict(filter(lambda x: x[0] != 'success', drinks.items()))


def get_purchase(pid):
    purchase = api.get('purchase', {'pid': pid})
    return purchase


def get_transaction(tid):
    transaction = api.get('transaction', {'tid': tid})
    return transaction


def add_drink(name, stock, price):
    api.create('drink', {
        'name': name,
        'stock': stock,
        'price': price
    })


def get_drink(did):
    drink = api.get('drink', {
        'did': did
    })
    return drink


def update_drink(did, name, stock, price):
    api.edit('drink', {'did': did}, {
        'name': name,
        'stock': stock,
        'price': price
    })


def create_drink(name, stock, price):
    api.create('drink', {
        'name': name,
        'stock': stock,
        'price': price
    })


def create_transaction(uid, amount, reason):
    date = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")

    api.create('transaction', {
        'datetime': date,
        'uid': uid,
        'amount': amount,
        'reason': reason
    })


def delete_drink(did):
    api.delete('drink', {'did': did})


def revert_purchase(pid):
    purchase = get_purchase(pid)[pid]
    user = User(uid=purchase['uid'])
    create_transaction(purchase['uid'], purchase['amount'], 'Kauferstattung')
    api.edit('user', {'uid': purchase['uid']}, {
        'balance': user.get_balance() + purchase['amount']
    })
    api.edit('drink', {'did': purchase['did']}, {
        'stock': get_drink(purchase['did'])[purchase['did']]['stock'] + 1
    })
    delete_purchase(pid)


def revert_transaction(tid):
    transaction = get_transaction(tid)
    api.edit('user', {'uid': transaction['uid']}, {
        'balance': user.get_balance() + purchase['amount']
    })

def delete_purchase(pid):
    api.delete('purchase', {'pid': pid})


def user_exists(badgenumber):
    badge = api.get('badge', {
        'badgenumber': badgenumber
    })
    return badge['success']
