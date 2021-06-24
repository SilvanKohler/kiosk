import datetime

default_avatar = 'https://www.sro.ch/typo3conf/ext/sro_template/Resources/Public/Images/favicon.ico'
api = None
def init(type_):
    global api
    if type_ == 'client':
        from _shared.api import API
        host = 'kassensystem.pythonanywhere.com'
        port = 443
        protocol = 'https'
        api = API(host, port, protocol)
    elif type_ == 'server':
        import _server.core as api


class User:
    def __init__(self, badgenumber=None, firstname=None, lastname=None, email=None, uid=None):
        self._uid = None
        if firstname is not None:
            self.register(firstname, lastname, email, badgenumber)
        elif badgenumber is not None:
            badges = api.get('badge', {
                'badgenumber': badgenumber
            })
            self.uid = list(dict(
                filter(lambda x: x[0] != 'success', dict(badges).items())).values())[0]['uid']
        elif uid is not None:
            self.uid = uid

    def register(self, firstname, lastname, email, badgenumber):
        users = get_users()
        for user in users.items():
            if user[1]['firstname'] == firstname and user[1]['lastname'] == lastname and user[1]['email'] == email:
                self.uid = user[0]
                break
        else:
            self.uid = api.create('user', {
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
                'avatar': default_avatar
            })['uid']
        api.create('badge', {
            'badgenumber': badgenumber,
            'uid': self.uid
        })

    @property
    def firstname(self):
        return api.get('user', {
            'uid': self.uid
        })[self.uid]['firstname']

    @property
    def lastname(self):
        return api.get('user', {
            'uid': self.uid
        })[self.uid]['lastname']

    @property
    def email(self):
        return api.get('user', {
            'uid': self.uid
        })[self.uid]['email']

    @property
    def balance(self):
        balance = 0
        transactions = self.get_transactions()
        purchases = self.get_purchases()
        for purchase in purchases.values():
            balance -= purchase['amount']
        for transaction in transactions.values():
            balance += transaction['amount']
        return balance

    @property
    def avatar(self):
        return api.get('user', {
            'uid': self.uid
        })[self.uid]['avatar']

    @property
    def badges(self):
        badges = api.get('badge', {
            'uid': self.uid
        })
        return [x['badgenumber'] for x in dict(filter(lambda x: x[0] != 'success', badges.items())).values()]

    @badges.setter
    def badges(self, badges):
        for badgenumber in badges:
            if not badgenumber in self.badges:
                api.create('badge', {
                    'badgenumber': badgenumber,
                    'uid': self.uid
                })

    @property
    def uid(self):
        if self._uid:
            return self._uid

    @uid.setter
    def uid(self, uid):
        self._uid = uid

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
        date = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        api.create('purchase', {
            'datetime': date,
            'did': did,
            'uid': self.uid,
            'amount': price
        })
        update_drink(did, drink['name'], drink['stock']-1, drink['price'])


def register_user(firstname, lastname, email, badgenumber):
    user = User(firstname=firstname, lastname=lastname,
                email=email, badgenumber=badgenumber)
    return user


def login_user(badgenumber):
    user = User(badgenumber=badgenumber)
    return user


def get_transactions(uid=None):
    transactions = api.get(
        'transaction', {'uid': uid} if uid is not None else {})
    return dict(filter(lambda x: x[0] != 'success', transactions.items()))


def get_purchases(uid=None):
    purchases = api.get('purchase', {'uid': uid} if uid is not None else {})
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
    api.edit('drink', {'did': purchase['did']}, {
        'stock': get_drink(purchase['did'])[purchase['did']]['stock'] + 1
    })
    delete_purchase(pid)


def delete_purchase(pid):
    api.delete('purchase', {'pid': pid})


def user_exists(badgenumber):
    badge = api.get('badge', {
        'badgenumber': badgenumber
    })
    return badge['success']
