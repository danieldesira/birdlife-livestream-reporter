import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def load_email_template():
    try:
        with open('email_template.html') as file:
            return file.read()
    except FileNotFoundError:
        print('email_template.html not found')


def generate_email_body(report_data: list):
    template = load_email_template()
    table_markup = ''.join(
        map(lambda
                stat: f"<tr><td><div class=\"rounded {stat.status.lower()}\"></div></td><td>{stat.name}</td><td>{stat.status}</td></tr>",
            report_data)
    )
    if any(filter(lambda stat: stat.status != 'Online', report_data)):
        total = len(report_data)
        online_count = len(list(filter(lambda stat: stat.status == 'Online', report_data)))
        summary = f"{online_count}/{total} livestreams online..."
    else:
        summary = 'All livestreams online!'
    return (template
            .replace('<!--report-->', table_markup)
            .replace('<!--summary-->', summary))


def send_email(report_data: list):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = os.getenv('MAIL_USERNAME')
        msg['To'] = os.getenv('MAIL_RECIPIENTS')
        msg['Subject'] = 'Birdlife Youtube Livestream Report'
        body = generate_email_body(report_data)
        msg.attach(MIMEText(body, 'html'))
        with smtplib.SMTP(os.getenv('MAIL_HOST'), int(os.getenv('MAIL_PORT') or '587')) as server:
            server.starttls()
            server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
            server.send_message(msg)
    except smtplib.SMTPException as e:
        print('Error: unable to send email', e)
