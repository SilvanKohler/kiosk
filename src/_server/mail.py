import smtplib
from email.message import EmailMessage
import _shared.data as data
import ssl
import configparser

cparser = configparser.ConfigParser()
cparser.read('config.ini')


def send(msg):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(cparser.get('credentials', 'smtp_host'), port=cparser.get('credentials', 'smtp_port'), context=context) as s:
        # s.starttls()
        s.login(cparser.get('credentials', 'smtp_username'),
                cparser.get('credentials', 'smtp_password'))
        s.send_message(msg)
        s.quit()


def send_expenses(usid):
    u = data.User(usid=usid)
    msg = EmailMessage()
    msg.set_content(
        f'''Hallo {u.firstname} {u.lastname}\nDu hast eine Balance von {u.balance} CHF.''')
    msg['Subject'] = f'Ausgabenbenachrichtigung'
    msg['From'] = cparser.get('credentials', 'smtp_sender')
    msg['To'] = u.email
    send(msg)


def send_stock(product):
    msg = EmailMessage()
    msg.set_content(
        f'''Hallo\nVom Produkt "{product['name']}" hat es noch {product['stock']} an Lager.''')
    msg['Subject'] = f'Lagerwarnung'
    msg['From'] = cparser.get('credentials', 'smtp_sender')
    msg['To'] = cparser.get('credentials', 'smtp_sender')
    send(msg)
