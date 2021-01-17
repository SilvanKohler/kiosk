import web, database, data
from time import sleep
from threading import Thread

web.get_transactions = data.get_transactions
web.get_drinks = data.get_drinks
web.update_drink = data.update_drink
Thread(target=database.run).start()
Thread(target=web.app.run, args=("0.0.0.0", 80)).start()
