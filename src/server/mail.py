import datetime
import smtplib
from email.message import EmailMessage
from multiprocessing import Pool, Process
from threading import Thread
from data import Customer
import time


sender = 'Kassensystem@Kassensystem'


def sendmail(UID):
    c = Customer(UID=UID)
    msg = EmailMessage()
    msg.set_content(
        f'''
Hallo {c.firstname} {c.lastname}
Du hast im letzten Monat {c.balance} CHF ausgegeben.''')
    msg['Subject'] = f'Ausgaben des letzten Monats'
    msg['From'] = sender
    msg['To'] = c.email
    s = smtplib.SMTP('raspberrypi', port=1025)
    s.send_message(msg)


def test():
    msg = EmailMessage()
    msg.set_content(
        f'''
    Hallo {"Silvan"} {"Kohler"}
    Du hast im letzten Monat {100} CHF ausgegeben.''')
    msg['Subject'] = f'Ausgaben des letzten Monats'
    msg['From'] = sender
    msg['To'] = 'edu.silvan.kohler@gmail.com'
    time.sleep(2)
    s = smtplib.SMTP('localhost', port=1025)
    s.send_message(msg)
