import shelve
import uuid
from collections import deque
from os import getcwd, mkdir, path 
from time import sleep
import directories

if not path.exists(directories.__data__):
    mkdir(directories.__data__)
user_table = shelve.open(path.join(directories.__data__, 'user'), writeback=True)
badge_table = shelve.open(path.join(directories.__data__, 'badge'), writeback=True)
product_table = shelve.open(path.join(directories.__data__, 'product'), writeback=True)
purchase_table = shelve.open(
    path.join(directories.__data__, 'purchase'), writeback=True)
transaction_table = shelve.open(
    path.join(directories.__data__, 'transaction'), writeback=True)

tables = {
    'user': user_table,
    'badge': badge_table,
    'product': product_table,
    'purchase': purchase_table,
    'transaction': transaction_table,
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
    print(i)
    queue.append(i)
    while queue[0] != i:
        print(queue)
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
