import smtplib
from email.message import EmailMessage
import _server.credentials as credentials
import _shared.data as data
import ssl


def send_expenses(usid):
    u = data.User(usid=usid)
    msg = EmailMessage()
    msg.set_content(
        f'''Hallo {u.firstname} {u.lastname}\nDu hast eine Balance von {u.balance} CHF.''')
    msg['Subject'] = f'Ausgabenbenachrichtigung'
    msg['From'] = credentials.sender
    msg['To'] = u.email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(credentials.smtp_host, port=credentials.smtp_port, context=context) as s:
        # s.starttls()
        s.login(credentials.smtp_username, credentials.smtp_password)
        s.send_message(msg)
        s.quit()


def send_stock(product):
    msg = EmailMessage()
    msg.set_content(
        f'''Hallo\nVom Produkt "{product['name']}" hat es noch {product['stock']} an Lager.''')
    msg['Subject'] = f'Lagerwarnung'
    msg['From'] = credentials.sender
    msg['To'] = credentials.sender
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(credentials.smtp_host, port=credentials.smtp_port, context=context) as s:
        # s.starttls()
        s.login(credentials.smtp_username, credentials.smtp_password)
        s.send_message(msg)
        s.quit()
