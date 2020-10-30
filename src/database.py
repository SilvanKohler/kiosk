import queue
import socketserver
import threading
import pickle
import shelve
import uuid
from time import sleep

customer_table = shelve.open('customer', writeback=True)  # UID: firstname, lastname, email, balance, avatar
badge_table = shelve.open('badge', writeback=True)  # BID: badge, FK_UID
drink_table = shelve.open('drink', writeback=True)  # DID: name, stock, price
purchase_table = shelve.open('purchase', writeback=True)  # PID: datetime, FK_DID, FK_UID
transaction_table = shelve.open('transaction', writeback=True)  # TID: datetime, FK_UID, amount
mail_table = shelve.open('mail', writeback=True)  # MID: datetime, FK_UID, balance

test_table = {}

tables = {'customer': customer_table, 'badge': badge_table, 'drink': drink_table, 'purchase': purchase_table,
          'transaction': transaction_table, 'mail': mail_table, 'test': test_table}

IP = '127.0.0.1'
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
                    id = uuid.uuid1().hex
                    chain.put(['get', s[1], id])
                    while not results.get(id, False):
                        sleep(0.1)
                    t = pickle.dumps(results.get(id, None))
                    self.request.send(t.__sizeof__())
                    self.request.send(t)
                elif s[0] == 'set':
                    chain.put(['set', s[1], s[2], s[3]])
                elif s[0] == 'del':
                    chain.put(['del', s[1], s[2]])
            else:
                print('Verbindung getrennt.')
                break


chain = queue.Queue()
results = {}

def process(request):
    if request[0] == 'get':
        results.update({request[2]: tables.get(request[1], None)})
    elif request[0] == 'set':
        tables.get(request[1], None)[request[2]] = request[3]
        tables.get(request[1], None).sync()
    elif request[0] == 'del':
        del tables.get(request[1], None)[request[2]]
        tables.get(request[1], None).sync()
    print(tables.get(request[1], None))


server = socketserver.ThreadingTCPServer((IP, PORT), RequestHandler)
server.serve_forever()
threading.Thread(target=server.serve_forever).start()
while True:
    while chain.unfinished_tasks > 0:
        process(chain.get())
        chain.task_done()
    sleep(0.05)
