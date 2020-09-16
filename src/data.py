import sqlite3
conn = sqlite3.connect('database.db')
c = conn.cursor()
def setup():
    c.execute('CREATE TABLE IF NOT EXISTS user (UID INT, firstname TEXT, lastname TEXT, email TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS badge (BID INT, badge INT, FK_UID INT)')
    c.execute('CREATE TABLE IF NOT EXISTS drink (DID INT, stock INT, price INT)')
    c.execute('CREATE TABLE IF NOT EXISTS transaction (TID INT, datetime TEXT, FK_DID INT, FK_UID INT)')
    conn.commit()
class User:
    def __init__(self, firstname, lastname, email, badge):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.balance = self.get_balance()
        self.avatar = self.get_avatar()
        self.uid = self.get_uid()
        self.badges = self.get_badges()
        self.check()
    def check(self):
        pass
        users = c.execute()
    def get_balance(self):
        pass
    def get_avatar(self):
        pass
    def get_badges(self):
        return c.execute(f'SELECT BID FROM badge WHERE FK_UID={self.uid}')
    def get_uid(self):
        return c.execute(f'SELECT UID FROM user WHERE firstname={self.firstname} AND lastname={self.lastname}')
    def withdraw(self, amount):
        pass
def create_user(firstname, lastname, email, badge):
    pass
    user = User(firstname, lastname, email, badge)