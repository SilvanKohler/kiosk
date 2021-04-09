import time
from threading import Thread

import web

t1 = Thread(target=web.tables.run)
t1.start()
t2 = Thread(target=web.app.run, args=("0.0.0.0", 80))
t2.start()

while True:
    web.tables.running = t2.is_alive()
    time.sleep(0.1)