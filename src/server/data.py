import datetime
import uuid
import socket
import pickle
from math import ceil, log

IP = '127.0.0.1'
PORT = 12345
blankprofile = 'https://murwillumbahvet.com.au/wp-content/uploads/2019/08/profile-blank.png'

blankprofile = 'https://media.giphy.com/media/QuPrp3BI6cMe2lErCb/giphy.gif'


class Customer:
    def __init__(self, badge=None, firstname=None, lastname=None, email=None, UID=None):
        if firstname is not None:
            self.firstname = firstname
            self.lastname = lastname
            self.email = email
            self.badges = [badge]
            self.register()
        if UID is not None:
            self.uid = UID
        else:
            self.badges = [badge]
            self.uid = self.get_uid()
        self.firstname = self.get_firstname()
        self.lastname = self.get_lastname()
        self.email = self.get_email()
        self.balance = self.get_balance()
        self.badges = self.get_badges()

    def register(self):
        global customer_table, badge_table
        exists = False
        for UID, (firstname, lastname, email, balance, avatar) in sorted(customer_table.items()):
            if (firstname, lastname, email) == (self.firstname, self.lastname, self.email):
                exists = True
                uid = UID
                break
        if not exists:
            uid = uuid.uuid1().hex
            customer_table[uid] = (self.firstname, self.lastname, self.email, 0, blankprofile)
        badge_table[uuid.uuid1().hex] = (self.badges[0], uid)

    def get_firstname(self):

        for UID, (firstname, lastname, email, balance, avatar) in sorted(customer_table.items()):
            if UID == self.uid:
                return firstname

    def get_lastname(self):

        for UID, (firstname, lastname, email, balance, avatar) in sorted(customer_table.items()):
            if UID == self.uid:
                return lastname

    def get_email(self):

        for UID, (firstname, lastname, email, balance, avatar) in sorted(customer_table.items()):
            if UID == self.uid:
                return email

    def get_balance(self):

        for UID, (firstname, lastname, email, balance, avatar) in sorted(customer_table.items()):
            if UID == self.uid:
                return balance

    def get_avatar(self):

        for UID, (firstname, lastname, email, balance, avatar) in sorted(customer_table.items()):
            if UID == self.uid:
                return avatar

    def get_badges(self):

        result = []
        for BID, (badge, FK_UID) in sorted(badge_table.items()):
            if FK_UID == self.uid:
                result.append(badge)
        return result

    def get_uid(self):

        for BID, (badge, FK_UID) in sorted(badge_table.items()):
            if badge == self.badges[0]:
                return FK_UID

    def get_transactions(self):

        result = []
        for PID, (dt, FK_DID, FK_UID) in sorted(purchase_table.items(), key=lambda x: x[1]):
            if FK_UID == self.uid:
                result.append((PID, dt, FK_DID, FK_UID))
        return result

    def withdraw(self, did):
        global drink_table, purchase_table, customer_table
        #
        price = drink_table[did][2]
        # print(customer_table[self.uid][3], price)
        customer_table[self.uid] = customer_table[self.uid][:3] + (customer_table[self.uid][3] + price,) + \
                                   customer_table[self.uid][
                                   4:]
        d = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        purchase_table[uuid.uuid1().hex] = (d, did, self.uid)
        drink_table[did] = (drink_table[did][0], drink_table[did][1] - 1, drink_table[did][2])


def get_transactions():
    transactions = []
    for PID, (dt, FK_DID, FK_UID) in sorted(purchase_table.items(), key=lambda x: x[1]):
        transaction = [dt, None, None, None]
        for UID, (firstname, lastname, email, balance, avatar) in sorted(customer_table.items()):
            if UID == FK_UID:
                transaction[1] = firstname + ' ' + lastname
        for DID, (name, stock, price) in sorted(drink_table.items()):
            if DID == FK_DID:
                transaction[2] = name
                transaction[3] = price
        transactions.append(transaction)
    return sorted(transactions, key=lambda x: x[0], reverse=True)


def register_customer(firstname, lastname, email, badge):
    customer = Customer(firstname=firstname, lastname=lastname, email=email, badge=badge)
    return customer


def login_customer(badge):
    customer = Customer(badge=badge)
    return customer


def get_drinks():
    result = []
    for DID, (name, stock, price) in sorted(drink_table.items()):
        result.append((DID, name, stock, price))
    return result


def add_drink(name, stock, price):
    global drink_table

    drink_table[uuid.uuid1().hex] = (name, stock, price)


def get_drink(did):
    for DID, (name, stock, price) in sorted(drink_table.items()):
        if DID == did:
            return name, stock, price


def customer_exists(b):
    for BID, (badge, FK_UID) in sorted(badge_table.items()):
        if badge == b:
            return True
    return False


def get_table(name):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('get')
    s.connect((IP, PORT))
    s.send(pickle.dumps(['get', name]))
    size = 2 ** ceil(log(int(str(s.recv(8), 'UTF-8'))) / log(2))
    t = s.recv(size)
    s.close()
    return pickle.loads(t)


def update_table(name, d):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('update')
    s.connect((IP, PORT))
    s.send(pickle.dumps(['update', name, d]))
    s.close()


def setitem_table(name, key, value):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('set')
    s.connect((IP, PORT))
    s.send(pickle.dumps(['set', name, key, value]))
    s.close()


def delitem_table(name, key):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('del')
    s.connect((IP, PORT))
    s.send(pickle.dumps(['set', name, key]))
    s.close()


class table(dict):
    def __init__(self, name):
        super().__init__()
        self.__dict = dict()
        self.name = name

    def __len__(self):
        self.sync()
        return self.__dict.__len__()

    def __getitem__(self, key):
        self.sync()
        return self.__dict.__getitem__(key)

    def __setitem__(self, key, value):
        setitem_table(self.name, key, value)
        self.sync()

    def __delitem__(self, key):
        delitem_table(self.name, key)
        self.sync()

    def __iter__(self):
        self.sync()
        return self.__dict.__iter__()

    def __contains__(self, item):
        self.sync()
        return self.__dict.__contains__(item)

    def sync(self):
        self.__dict = get_table(self.name)

    def items(self):
        self.sync()
        return self.__dict.items()

    def update(self, d):
        self.table = update_table(self.name, d)

    def get(self, key, default):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


customer_table = table('customer')  # UID: firstname, lastname, email, balance, avatar
badge_table = table('badge')  # BID: badge, FK_UID
drink_table = table('drink')  # DID: name, stock, price
purchase_table = table('purchase')  # PID: datetime, FK_DID, FK_UID
transaction_table = table('transaction')  # TID: datetime, FK_UID, amount
mail_table = table('mail')  # MID: datetime, FK_UID, balance
