import smtplib
from email.message import EmailMessage
import _shared.data as data
import ssl
import configparser

cparser = configparser.ConfigParser()
cparser.read(['default_config.ini', 'config.ini'])


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
        f'''Hallo {u.firstname} {u.lastname}\nDein Guthaben beträgt {u.balance} CHF.\nDein Guthaben kannst Du via TWINT ({cparser.get('contact', 'twint_number')}) oder Bar an {cparser.get('contact', 'name')} aufladen.\n\nVielen Dank.\n\nAntworten werden an {cparser.get('contact', 'name')} weitergeleitet.''')
    msg['Subject'] = f'Guthabenbenachrichtigung'
    msg['From'] = cparser.get('credentials', 'smtp_sender')
    msg['To'] = u.email
    send(msg)


def send_stock(product):
    msg = EmailMessage()
    msg.set_content(
        f'''Hallo\nVom Produkt "{product['name']}" hat es noch {product['stock']} an Lager.\nAlle Produkte: {cparser.get('client', 'protocol')}://{cparser.get('client', 'host')}:{cparser.get('client', 'port')}/products''')
    msg['Subject'] = f'Lagerwarnung'
    msg['From'] = cparser.get('credentials', 'smtp_sender')
    msg['To'] = cparser.get('credentials', 'smtp_sender')
    send(msg)
