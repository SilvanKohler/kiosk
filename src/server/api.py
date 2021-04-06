import requests


class API:
    def __init__(self, ip, port, protocol='https'):
        self.ip = ip
        self.port = port
        self.protocol = protocol

    @property
    def url(self):
        return f'{self.protocol}://{self.ip}:{self.port}/api'

    def get(self, table, filters):
        return requests.post(f'{self.url}/{table}/get', data=filters).json()

    def create(self, table, properties):
        return requests.post(f'{self.url}/{table}/create', data=properties).json()

    def edit(self, table, filters, properties):
        return requests.post(f'{self.url}/{table}/edit',
                             data=dict(tuple(filters.items()) + tuple(properties.items()))).json()

    def delete(self, table, filters):
        return requests.post(f'{self.url}/{table}/delete', data=filters).json()


if __name__ == '__main__':
    api = API('localhost', 80, 'http')
    users = api.get('user', {})
    print(users)
    user = input('delete: ')
    print(api.delete('user', {'uid': user}))

