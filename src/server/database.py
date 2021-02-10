import queue
import socketserver
import threading
import pickle
import shelve
import uuid
from time import sleep

data_directory = 'data/'

customer_table = shelve.open(data_directory + 'customer', writeback=True)  # UID: firstname, lastname, email, balance, avatar
badge_table = shelve.open(data_directory + 'badge', writeback=True)  # BID: badge, FK_UID
drink_table = shelve.open(data_directory + 'drink', writeback=True)  # DID: name, stock, price
purchase_table = shelve.open(data_directory + 'purchase', writeback=True)  # PID: datetime, FK_DID, FK_UID
transaction_table = shelve.open(data_directory + 'transaction', writeback=True)  # TID: datetime, FK_UID, amount
mail_table = shelve.open(data_directory + 'mail', writeback=True)  # MID: datetime, FK_UID, balance

test_table = shelve.open(data_directory + 'test', writeback=True)

tables = {'customer': customer_table, 'badge': badge_table, 'drink': drink_table, 'purchase': purchase_table,
          'transaction': transaction_table, 'mail': mail_table, 'test': test_table}
for table in tables.values():
    print('\n'.join(f'{x}: {y}' for x, y in table.items()))
IP = '0.0.0.0'
PORT = 12345
CHUNK = 2048


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        addr = self.client_address[0]
        print('Verbindung hergestellt.')
        while True:
            s = self.request.recv(CHUNK)
            if s:
                s = pickle.loads(s)
                print(s)
                if s[0] == 'get':
                    i = uuid.uuid1().hex
                    chain.put(['get', s[1], i])
                    while results.get(i, None) is None:
                        sleep(0.05)
                    t = pickle.dumps(results.get(i, None))
                    self.request.send(bytes(str(t.__sizeof__()), 'UTF-8'))
                    # print(bytes(str(t.__sizeof__()), 'UTF-8'))
                    sleep(0.1)
                    print("----------------------------")
                    print(t)
                    self.request.send(t)
                elif s[0] == 'set':
                    chain.put(['set', s[1], s[2], s[3]])
                elif s[0] == 'update':
                    chain.put(['update', s[1], s[2]])
                elif s[0] == 'del':
                    chain.put(['del', s[1], s[2]])
            else:
                print('Verbindung getrennt.')
                break

chain = queue.Queue()
results = {}


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


server = socketserver.ThreadingTCPServer((IP, PORT), RequestHandler)
# server.serve_forever()
stopped = False


def start():
    global stopped
    try:
        server.serve_forever()
    except Exception as e:
        print(e)
        stopped = True
    for table in tables.values():
        if isinstance(table, shelve.Shelf):
            table.sync()
            table.close()

def run():
    threading.Thread(target=start).start()
    print('Server gestartet.')
    while not stopped:
        # print('Warteschlange abarbeiten.')
        while chain.unfinished_tasks > 0 and not stopped:
            print(f'Anfrage abarbeiten.')
            process(chain.get())
            chain.task_done()
            print(f'Anfrage fertig.')
        # print('Warteschlange leer.')
        sleep(0.05)
    server.shutdown()
