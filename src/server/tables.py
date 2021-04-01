import queue
import socketserver
import threading
import shelve
import uuid
from time import sleep


data_directory = 'data/'

customer_table = shelve.open(data_directory + 'user', writeback=True)
badge_table = shelve.open(data_directory + 'badge', writeback=True)
drink_table = shelve.open(data_directory + 'drink', writeback=True)
purchase_table = shelve.open(data_directory + 'purchase', writeback=True)
transaction_table = shelve.open(data_directory + 'transaction', writeback=True)
mail_table = shelve.open(data_directory + 'mail', writeback=True)

tables = {
    'user': customer_table,
    'badge': badge_table,
    'drink': drink_table,
    'purchase': purchase_table,
    'transaction': transaction_table,
    'mail': mail_table
}
for table in tables.values():
    print('\n'.join(f'{x}: {y}' for x, y in table.items()))

chain = queue.Queue()
results = {}
running = True

def process(request):
    print(1, request)
    if request[0] == 'get':
        print(2, {request[2]: dict(tables.get(request[1], None).items())})
        results.update({request[2]: dict(tables.get(request[1], None).items())})
    elif request[0] == 'set':
        tables.get(request[1], None)[request[2]] = request[3]
        if isinstance(tables.get(request[1], None), shelve.Shelf):
            tables.get(request[1], None).sync()
    elif request[0] == 'update':
        tables.get(request[1], {}).update(request[2])
        if isinstance(tables.get(request[1], None), shelve.Shelf):
            tables.get(request[1], None).sync()
    elif request[0] == 'del':
        del tables.get(request[1], None)[request[2]]
        if isinstance(tables.get(request[1], None), shelve.Shelf):
            tables.get(request[1], None).sync()
    print(3, dict(tables.get(request[1], None).items()))

def run():
    print('Server gestartet.')
    while running:
        # print('Warteschlange abarbeiten.')
        while chain.unfinished_tasks > 0:
            print(f'Anfrage abarbeiten.')
            process(chain.get())
            chain.task_done()
            print(f'Anfrage fertig.')
        # print('Warteschlange leer.')
        sleep(0.05)
