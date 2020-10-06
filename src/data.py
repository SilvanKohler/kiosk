import shelve
import datetime
import uuid

blankprofile = 'https://murwillumbahvet.com.au/wp-content/uploads/2019/08/profile-blank.png'
# blankprofile = 'https://media.giphy.com/media/3o6fJ47Uq6jMb1OULu/giphy.gif'

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
        for PID, (dt, FK_DID, FK_UID) in sorted(purchase_table.items()):
            if FK_UID == self.uid:
                result.append((PID, dt, FK_DID, FK_UID))
        return result

    def withdraw(self, did):
        price = drink_table[did][2]
        print(customer_table[self.uid][3], price)
        customer_table[self.uid] = customer_table[self.uid][:3] + (customer_table[self.uid][3] + price,) + customer_table[self.uid][
                                                                                            4:]
        d = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        purchase_table[uuid.uuid1().hex] = (d, did, self.uid)
        drink_table[did] = (drink_table[did][0], drink_table[did][1]-1, drink_table[did][2])



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


customer_table = shelve.open('customer')  # UID: firstname, lastname, email, balance, avatar
badge_table = shelve.open('badge')  # BID: badge, FK_UID
drink_table = shelve.open('drink')  # DID: name, stock, price
purchase_table = shelve.open('purchase')  # PID: datetime, FK_DID, FK_UID
transaction_table = shelve.open('transaction')  # TID: datetime, FK_UID, amount
mail_table = shelve.open('mail')  # MID: datetime, FK_UID, balance


def close():
    customer_table.close()
    badge_table.close()
    drink_table.close()
    purchase_table.close()
    transaction_table.close()
    mail_table.close()


def init():
    drink_table.clear()
    drink_table[uuid.uuid1().hex] = ('Kaffee', 40, .5)
    drink_table[uuid.uuid1().hex] = ('Cola', 10, 1)
    drink_table[uuid.uuid1().hex] = ('Energy Drink', 10, 1)


# init()

# import sqlite3
# import datetime
#
#
# def setup():
#     c.execute(
#         'CREATE TABLE IF NOT EXISTS "customer" ("UID" INT PRIMARY KEY, "firstname" TEXT, "lastname" TEXT, "email" TEXT, "balance" INT, "avatar" TEXT)')
#     c.execute('CREATE TABLE IF NOT EXISTS "badge" ("BID" INT PRIMARY KEY, "badge" INT, "FK_UID" INT)')
#     c.execute('CREATE TABLE IF NOT EXISTS "drink" ("DID" INT PRIMARY KEY, "name" TEXT, "stock" INT, "price" INT)')
#     c.execute(
#         'CREATE TABLE IF NOT EXISTS "purchase" ("PID" INT PRIMARY KEY, "datetime" TEXT, "FK_DID" INT, "FK_UID" INT)')
#     conn.commit()
#
#
# class Customer:
#     def __init__(self, badge, firstname=None, lastname=None, email=None):
#         if firstname is not None:
#             self.firstname = firstname
#             self.lastname = lastname
#             self.email = email
#             self.badges = [badge]
#             self.register()
#         self.badges = [badge]
#         self.uid = self.get_uid()
#         self.firstname = self.get_firstname()
#         self.lastname = self.get_lastname()
#         self.email = self.get_email()
#         self.balance = self.get_balance()
#         self.avatar = self.get_avatar()
#         self.badges = self.get_badges()
#
#     def register(self):
#         c.execute(
#             f'''SELECT "UID" from "customer" WHERE "firstname"='{self.firstname}' AND "lastname"='{self.lastname}' AND "email"='{self.email}' ''')
#         if c.rowcount == -1:
#             c.execute(
#                 f'''INSERT INTO "customer" ("firstname", "lastname", "email", "balance", "avatar") VALUES ('{self.firstname}', '{self.lastname}', '{self.email}', '{0}', '{"https://serc.carleton.edu/download/images/54334/empty_user_icon_256.v2.png"}')''')
#             conn.commit()
#             # print(c.lastrowid)
#         #     c.execute(f'INSERT INTO badge (badge, FK_UID) VALUES ({self.badges[0]}, {c.lastrowid})')
#         # else:
#         c.execute(f'''INSERT INTO "badge" ("badge", "FK_UID") VALUES ('{self.badges[0]}', '{self.get_uid()}')''')
#         conn.commit()
#
#     def get_balance(self):
#         c.execute(f'''SELECT "balance" FROM "customer" WHERE "UID"='{self.uid}' ''')
#         return c.fetchone()
#
#     def get_avatar(self):
#         c.execute(f'''SELECT "avatar" FROM "customer" WHERE "UID"='{self.uid}' ''')
#         return c.fetchone()
#
#     def get_badges(self):
#         c.execute(f'''SELECT "BID" FROM "badge" WHERE "FK_UID"='{self.uid}' ''')
#         return c.fetchall()
#
#     def get_uid(self):
#         c.execute(
#             f'''SELECT "FK_UID" FROM "badge" WHERE "badge"='{self.badges[0]}' ''')
#         if c.rowcount == -1:
#             c.execute(
#                 f'''SELECT "UID" from "customer" WHERE "firstname"='{self.firstname}' AND "lastname"='{self.lastname}' AND "email"='{self.email}' ''')
#         return c.fetchone()
#
#     def get_firstname(self):
#         print(f'''SELECT "firstname" FROM "customer" WHERE "UID"='{self.uid}' ''')
#         c.execute(f'''SELECT "firstname" FROM "customer" WHERE "UID"='{self.uid}' ''')
#         return c.fetchone()
#
#     def get_lastname(self):
#         c.execute(f'''SELECT "lastname" FROM "customer" WHERE "UID"='{self.uid}' ''')
#         return c.fetchone()
#
#     def get_email(self):
#         c.execute(f'''SELECT "email" FROM "customer" WHERE "UID"='{self.uid}' ''')
#         return c.fetchone()
#
#     def withdraw(self, did, amount):
#         c.execute(f'''UPDATE "customer" SET "balance"='{self.balance + amount}' WHERE "UID"='{self.uid}' ''')
#         d = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
#         c.execute(f'''INSERT INTO "purchase" ("datetime", "FK_DID", "FK_UID") VALUES ('{d}', '{did}', '{self.uid}')''')
#         conn.commit()
#
#
# def register_customer(firstname, lastname, email, badge):
#     customer = Customer(firstname=firstname, lastname=lastname, email=email, badge=badge)
#     return customer
#
#
# def login_customer(badge):
#     customer = Customer(badge=badge)
#     return customer
#
#
# def get_drinks():
#     c.execute(f'SELECT (BID, name, price) FROM drink')
#     return c.fetchall()
#
#
# def get_purchases(uid):
#     c.execute(f'SELECT * FROM purchase WHERE FK_UID={uid}')
#     return c.fetchall()
#
#
# def customer_exists(badge):
#     c.execute(f'SELECT BID FROM badge WHERE badge={badge}')
#     if c.rowcount == -1:
#         return False
#     else:
#         return True
#
#
# conn = sqlite3.connect('database.db', check_same_thread=False)
# c = conn.cursor()
# setup()
