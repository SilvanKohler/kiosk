import queue
import socketserver
import threading
import pickle
import shelve

customer_table = shelve.open('customer', writeback=True)  # UID: firstname, lastname, email, balance, avatar
badge_table = shelve.open('badge', writeback=True)  # BID: badge, FK_UID
drink_table = shelve.open('drink', writeback=True)  # DID: name, stock, price
purchase_table = shelve.open('purchase', writeback=True)  # PID: datetime, FK_DID, FK_UID
transaction_table = shelve.open('transaction', writeback=True)  # TID: datetime, FK_UID, amount
mail_table = shelve.open('mail', writeback=True)  # MID: datetime, FK_UID, balance

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
                    pass
            else:
                print('Verbindung getrennt.')
                break


chain = queue.Queue()
server = socketserver.ThreadingTCPServer((IP, PORT), RequestHandler)
server.serve_forever()
