import requests


class API:
    def __init__(self, ip, port=443, protocol='https'):
        self.ip = ip
        self.port = port
        self.protocol = protocol

    @property
    def url(self):
        return f'{self.protocol}://{self.ip}:{self.port}/api'

    def get(self, table, filters):
        print(table, filters)
        r = requests.post(f'{self.url}/{table}/get', data=filters)
        print(r.content)
        return r.json()

    def create(self, table, properties):
        print(table, properties)
        return requests.post(f'{self.url}/{table}/create', data=properties).json()

    def edit(self, table, filters, properties):
        return requests.post(f'{self.url}/{table}/edit',
                             data=dict(tuple(filters.items()) + tuple(properties.items()))).json()

    def delete(self, table, filters):
        return requests.post(f'{self.url}/{table}/delete', data=filters).json()


if __name__ == '__main__':
    import datetime
    # host = 'kassensystem.pythonanywhere.com'
    # port = 443
    # protocol = 'https'
    host = 'localhost'
    port = 80
    protocol = 'http'
    api = API(host, port, protocol)
    drinks = api.get('drink', {})
    print(dict(filter(lambda x: x[0] != 'success', drinks.items())))
    for x in range(1000):
        print(x)
        date = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        api.create('transaction', {
            'datetime': date,
            'uid': 'b378fb5dd03b11eb848918cc18e03914',
            'amount': 1,
            'reason': 'performance-test'
        })
