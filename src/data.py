
class User:
    def __init__(self, firstname, lastname, email):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.balance = self.get_balance()
        self.avatar = self.get_avatar()
    def get_balance(self):
        pass
    def get_avatar(self):
        pass
    def withdraw(self, amount):
        pass