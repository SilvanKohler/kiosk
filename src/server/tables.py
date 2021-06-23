from collections import deque
import shelve
from time import sleep
import uuid
data_directory = 'data/'

user_table = shelve.open(data_directory + 'user', writeback=True)
badge_table = shelve.open(data_directory + 'badge', writeback=True)
drink_table = shelve.open(data_directory + 'drink', writeback=True)
purchase_table = shelve.open(data_directory + 'purchase', writeback=True)
transaction_table = shelve.open(data_directory + 'transaction', writeback=True)
mail_table = shelve.open(data_directory + 'mail', writeback=True)

tables = {
    'user': user_table,
    'badge': badge_table,
    'drink': drink_table,
    'purchase': purchase_table,
    'transaction': transaction_table,
    'mail': mail_table
}
for table in tables.items():
    print(table[0] + ':')
    print('\n'.join(f'{x}: {y}' for x, y in table[1].items()))

queue = deque()


def sync(table):
    if isinstance(tables.get(table, None), shelve.Shelf):
        tables.get(table, None).sync()


def get(table):
    i = uuid.uuid1().hex
    queue.append(i)
    while queue[0] != i:
        sleep(0.1)
    result = dict(tables.get(table, None).items())
    sync(table)
    queue.popleft()
    return result


def set(table, key, value):
    i = uuid.uuid1().hex
    queue.append(i)
    while queue[0] != i:
        sleep(0.1)
    tables.get(table, None)[key] = value
    sync(table)
    queue.popleft()


def update(table, dict_):
    i = uuid.uuid1().hex
    queue.append(i)
    while queue[0] != i:
        sleep(0.1)
    tables.get(table, {}).update(dict_)
    sync(table)
    queue.popleft()


def delete(table, key):
    i = uuid.uuid1().hex
    queue.append(i)
    while queue[0] != i:
        sleep(0.1)
    del tables.get(table, None)[key]
    sync(table)
    queue.popleft()