import smtplib
import ssl
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send(receiver_email, text, html):
    with open('credentials.json', 'r') as file:
        credentials = json.load(file)
    credentials = credentials['mail']

    # Create a secure SSL context
    context = ssl.create_default_context()

    message = MIMEMultipart("alternative")
    message["Subject"] = "[HPKCHC] Stats"
    message["From"] = credentials['email']
    message["To"] = receiver_email

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP_SSL(credentials['smtp'], credentials['port'], context=context) as server:
        server.login(credentials['login'], credentials['password'])
        server.sendmail(credentials['email'], receiver_email, message.as_string())

    print("Mail sent.")


def main():
    # Create the plain-text and HTML version of your message
    text = """\
    Hi,
    How are you?
    Real Python has many great tutorials:
    www.realpython.com"""
    html = """\
    <html>
    <body>
        <p>Hi,<br>
        How are you?<br>
        <a href="http://www.realpython.com">Real Python</a>
        has many great tutorials.
        </p>
    </body>
    </html>
    """
    to = 'a@b.com'

    send(to, text, html)


if __name__ == '__main__':
    main()
