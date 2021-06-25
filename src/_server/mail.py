import datetime
import smtplib
from email.message import EmailMessage
from multiprocessing import Pool, Process
from threading import Thread
from _shared.data import User
import time


sender = 'Kassensystem@Kassensystem'


def sendmail(usid):
    u = User(usid=usid)
    msg = EmailMessage()
    msg.set_content(
        f'''
Hallo {u.firstname} {u.lastname}
Du hast im letzten Monat {u.balance} CHF ausgegeben.''')
    msg['Subject'] = f'Ausgaben des letzten Monats'
    msg['From'] = sender
    msg['To'] = u.email
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
    msg['To'] = 'silvankohler@protonmail.com'
    time.sleep(2)
    s = smtplib.SMTP('localhost', port=1025)
    s.send_message(msg)
