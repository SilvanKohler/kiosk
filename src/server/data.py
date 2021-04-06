import datetime

from api import API

default_avatar = 'https://murwillumbahvet.com.au/wp-content/uploads/2019/08/profile-blank.png'

# default_avatar = 'https://media.giphy.com/media/QuPrp3BI6cMe2lErCb/giphy.gif'


specs = {
    'user': ('uid', ('firstname', 'lastname', 'email', 'balance', 'avatar')),
    'badge': ('bid', ('badgenumber', 'uid')),
    'drink': ('did', ('name', 'stock', 'price')),
    'purchase': ('pid', ('datetime', 'did', 'uid', 'amount')),
    'transaction': ('tid', ('datetime', 'uid', 'amount')),
    'mail': ('mid', ('datetime', 'uid', 'balance'))
}

api = API('127.0.0.1', 80, 'http')


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
        api.create('user', {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'balance': 0.0,
            'avatar': default_avatar
        })

    def get_firstname(self):
        return api.get('user', {
            'uid': self.uid
        })['firstname']

    def get_lastname(self):
        return api.get('user', {
            'uid': self.uid
        })['lastname']

    def get_email(self):
        return api.get('user', {
            'uid': self.uid
        })['email']

    def get_balance(self):
        return api.get('user', {
            'uid': self.uid
        })['balance']

    def get_avatar(self):
        return api.get('user', {
            'uid': self.uid
        })['avatar']

    def get_badges(self):
        badges = api.get('badge', {
            'uid': self.uid
        })
        return [x['badgenumber'] for x in dict(filter(lambda x: x[0] != 'success', badges.items())).values()]

    def get_uid(self):  # From badge number
        badges = api.get('badge', {
            'uid': self.uid
        })
        return dict(filter(lambda x: x[0] != 'success', badges.items())).values()[0]['uid']

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

    def withdraw(self, did):
        drink = get_drink(did)
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


def get_all_transactions():
    transactions = api.get('transaction', {})
    return dict(filter(lambda x: x[0] != 'success', transactions.items()))


def register_user(firstname, lastname, email, badgenumber):
    user = User(firstname=firstname, lastname=lastname, email=email, badgenumber=badgenumber)
    return user


def login_user(badgenumber):
    user = User(badgenumber=badgenumber)
    return user


def get_drinks():
    drinks = api.get('drink', {})
    return dict(filter(lambda x: x[0] != 'success', drinks.items()))


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


def user_exists(badgenumber):
    badge = api.get('badge', {
        'badgenumber': badgenumber
    })
