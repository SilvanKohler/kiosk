import datetime
import random

default_avatar = 'https://www.sro.ch/typo3conf/ext/sro_template/Resources/Public/Images/favicon.ico'
api = None


def init(type_):
    global api
    if type_ == 'client':
        from _shared.api import API
        # host = 'kassensystem.pythonanywhere.com'
        # port = 443
        # protocol = 'https'
        host = '192.168.78.216'
        port = 80
        protocol = 'http'
        api = API(host, port, protocol)
    elif type_ == 'server':
        import _server.core as api


class User:
    def __init__(self, badgenumber=None, firstname=None, lastname=None, email=None, usid=None):
        self._usid = None
        if firstname is not None:
            self.register(firstname, lastname, email, badgenumber)
        elif badgenumber is not None:
            badges = api.get('badge', {
                'badgenumber': badgenumber
            })
            self.usid = list(dict(
                filter(lambda x: x[0] != 'success', dict(badges).items())).values())[0]['usid']
        elif usid is not None:
            self.usid = usid

    def register(self, firstname, lastname, email, badgenumber):
        users = get_users()
        for user in users.items():
            if user[1]['firstname'] == firstname and user[1]['lastname'] == lastname and user[1]['email'] == email:
                self.usid = user[0]
                break
        else:
            self.usid = api.create('user', {
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
                'avatar': default_avatar
            })['usid']
        api.create('badge', {
            'badgenumber': badgenumber,
            'usid': self.usid
        })

    @property
    def firstname(self):
        return api.get('user', {
            'usid': self.usid
        })[self.usid]['firstname']

    @property
    def lastname(self):
        return api.get('user', {
            'usid': self.usid
        })[self.usid]['lastname']

    @property
    def email(self):
        return api.get('user', {
            'usid': self.usid
        })[self.usid]['email']

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
            'usid': self.usid
        })[self.usid]['avatar']

    @property
    def badges(self):
        badges = api.get('badge', {
            'usid': self.usid
        })
        return [x['badgenumber'] for x in dict(filter(lambda x: x[0] != 'success', badges.items())).values()]

    @badges.setter
    def badges(self, badges):
        for badgenumber in badges:
            if not badgenumber in self.badges:
                api.create('badge', {
                    'badgenumber': badgenumber,
                    'usid': self.usid
                })

    @property
    def usid(self):
        if self._usid:
            return self._usid

    @usid.setter
    def usid(self, usid):
        self._usid = usid

    @property
    def otp(self):
        date = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        otid = api.create('otp', {
            'datetime': date,
            'otp': random.randint(100000, 999999),
            'usid': self.usid
        })['otid']
        otp = api.get('otp', {
            'otid': otid
        })
        return dict(filter(lambda x: x[0] != 'success', otp.items()))[otid]['otp']

    def get_purchases(self):
        purchases = api.get('purchase', {
            'usid': self.usid
        })
        return dict(filter(lambda x: x[0] != 'success', purchases.items()))

    def get_transactions(self):
        transactions = api.get('transaction', {
            'usid': self.usid
        })
        return dict(filter(lambda x: x[0] != 'success', transactions.items()))

    def buy(self, prid):
        product = get_product(prid)[prid]
        price = product['price']
        date = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        api.create('purchase', {
            'datetime': date,
            'prid': prid,
            'usid': self.usid,
            'amount': price
        })
        update_product(prid, product['name'],
                       product['stock']-1, product['price'])


def register_user(firstname, lastname, email, badgenumber):
    user = User(firstname=firstname, lastname=lastname,
                email=email, badgenumber=badgenumber)
    return user


def login_user(badgenumber):
    user = User(badgenumber=badgenumber)
    return user


def get_transactions(usid=None):
    transactions = api.get(
        'transaction', {'usid': usid} if usid is not None else {})
    return dict(filter(lambda x: x[0] != 'success', transactions.items()))


def get_purchases(usid=None):
    purchases = api.get('purchase', {'usid': usid} if usid is not None else {})
    return dict(filter(lambda x: x[0] != 'success', purchases.items()))


def get_users():
    users = api.get('user', {})
    return dict(filter(lambda x: x[0] != 'success', users.items()))


def get_badges():
    badges = api.get('badge', {})
    return dict(filter(lambda x: x[0] != 'success', badges.items()))


def get_products():
    products = api.get('product', {})
    return dict(filter(lambda x: x[0] != 'success', products.items()))


def get_purchase(puid):
    purchase = api.get('purchase', {'puid': puid})
    return purchase


def get_transaction(trid):
    transaction = api.get('transaction', {'trid': trid})
    return transaction


def get_product(prid):
    product = api.get('product', {
        'prid': prid
    })
    return product


def update_product(prid, name, stock, price):
    api.edit('product', {'prid': prid}, {
        'name': name,
        'stock': stock,
        'price': price
    })


def create_product(name, stock, price):
    api.create('product', {
        'name': name,
        'stock': stock,
        'price': price
    })


def create_transaction(usid, amount, reason):
    date = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")

    api.create('transaction', {
        'datetime': date,
        'usid': usid,
        'amount': amount,
        'reason': reason
    })


def delete_product(prid):
    api.delete('product', {'prid': prid})


def revert_purchase(puid):
    purchase = get_purchase(puid)[puid]
    api.edit('product', {'prid': purchase['prid']}, {
        'stock': get_product(purchase['prid'])[purchase['prid']]['stock'] + 1
    })
    delete_purchase(puid)


def delete_purchase(puid):
    api.delete('purchase', {'puid': puid})


def user_exists(badgenumber):
    badge = api.get('badge', {
        'badgenumber': badgenumber
    })
    return badge['success']


def check_otp(pin):
    otp = api.get('otp', {'otp': pin})
    if otp['success']:
        api.delete('otp', {'otid': list(dict(filter(lambda x: x[0] != 'success', dict(otp).items())).keys())[0]})
        if datetime.datetime.now() - datetime.datetime.strptime(list(dict(filter(lambda x: x[0] != 'success', dict(otp).items())).values())[0]['datetime'], "%d-%m-%Y_%H:%M:%S") <= datetime.timedelta(minutes=10):
            user = api.get('user', {'usid': list(dict(
                filter(lambda x: x[0] != 'success', dict(otp).items())).values())[0]['usid']})
            return list(dict(filter(lambda x: x[0] != 'success', dict(user).items())).values())[0]['level']
        else:
            return 0
    else:
        return 0

def test():
    init('client')
    user = User(0, 'Silvan', 'Kohler', 's.kohler@sro.ch')
    print(user.otp)
