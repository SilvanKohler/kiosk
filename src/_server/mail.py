import smtplib
from email.message import EmailMessage
import _server.credentials as credentials
import _shared.data as data
import ssl


def send(usid):
    u = data.User(usid=usid)
    msg = EmailMessage()
    msg.set_content(f'''Hallo {u.firstname} {u.lastname}\nDu hast im letzten Monat {u.balance} CHF ausgegeben.''')
    msg['Subject'] = f'Ausgaben des letzten Monats'
    msg['From'] = credentials.sender
    msg['To'] = u.email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(credentials.smtp_host, port=credentials.smtp_port, context=context) as s:
        # s.starttls()
        s.login(credentials.smtp_username, credentials.smtp_password)
        s.send_message(msg)
        s.quit()

def test():
    msg = EmailMessage()
    msg.set_content(f'''Hallo Silvan Kohler\nDu hast im letzten Monat 100.00 CHF ausgegeben.''')
    msg['Subject'] = f'Ausgaben des letzten Monats'
    msg['From'] = credentials.sender
    msg['To'] = 'silvankohler@protonmail.com'
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(credentials.smtp_host, port=credentials.smtp_port, context=context) as s:
        # s.starttls()
        s.login(credentials.smtp_username, credentials.smtp_password)
        s.send_message(msg)
        s.quit()