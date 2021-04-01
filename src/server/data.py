import datetime
import uuid

IP = '127.0.0.1'
PORT = 80

blankprofile = 'https://murwillumbahvet.com.au/wp-content/uploads/2019/08/profile-blank.png'

# blankprofile = 'https://media.giphy.com/media/QuPrp3BI6cMe2lErCb/giphy.gif'

specs = {
    'user': ('uid', ('firstname', 'lastname', 'email', 'balance', 'avatar')),
    'badge': ('bid', ('badge', 'uid')),
    'drink': ('did', ('name', 'stock', 'price')),
    'purchase': ('pid', ('datetime', 'did', 'uid', 'amount')),
    'transaction': ('tid', ('datetime', 'uid', 'amount')),
    'mail': ('mid', ('datetime', 'uid', 'balance'))
}


class User:
    def __init__(self, badge=None, firstname=None, lastname=None, email=None, uid=None):
        if firstname is not None:
            self.firstname = firstname
            self.lastname = lastname
            self.email = email
            self.badges = [badge]
            self.register()
        if uid is not None:
            self.uid = uid
        else:
            self.badges = [badge]
            self.uid = self.get_uid()
        self.firstname = self.get_firstname()
        self.lastname = self.get_lastname()
        self.email = self.get_email()
        self.balance = self.get_balance()
        self.badges = self.get_badges()

    def register(self):
        pass

    def get_firstname(self):
        pass

    def get_lastname(self):
        pass

    def get_email(self):
        pass

    def get_balance(self):
        pass

    def get_avatar(self):
        pass

    def get_badges(self):
        pass

    def get_uid(self):  # From badge number
        pass

    def get_purchases(self):
        pass

    def get_transactions(self):
        pass

    def withdraw(self, did):  # d = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        pass


def get_all_transactions():
    pass

def register_user(firstname, lastname, email, badge):
    user = User(firstname=firstname, lastname=lastname, email=email, badge=badge)
    return user


def login_user(badge):
    user = User(badge=badge)
    return user


def get_drinks():
    pass


def add_drink(name, stock, price):
    pass


def get_drink(did):
    pass

def update_drink(DID, name, stock, price):
    pass


def customer_exists(b):
    pass