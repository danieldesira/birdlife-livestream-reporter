import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Literal

logger = logging.getLogger(__name__)


def load_email_template(html_template: Literal['email_template.html', 'youtube_api_error.html']):
    try:
        with open(f'templates/{html_template}') as file:
            return file.read()
    except FileNotFoundError as e:
        logger.error(f'{html_template} not found')
        raise e


def generate_email_body(template: str, report_data: list):
    table_markup = ''.join(
        map(lambda
                stat: f"<tr><td><div class=\"rounded {stat.status.lower()}\"></div></td><td><a href=\"{stat.url}\">{stat.name}</a></td><td><span class=\"{stat.status.lower()}-text\">{stat.status}</span></td></tr>",
            report_data)
    )
    if any(filter(lambda stat: stat.status != 'Online', report_data)):
        total = len(report_data)
        online_count = len(list(filter(lambda stat: stat.status == 'Online', report_data)))
        summary = f"{online_count}/{total} livestreams are online. Please check the report below for more details."
    else:
        summary = 'All livestreams are online!'
    if template:
        return (template
                .replace('<!--report-->', table_markup)
                .replace('<!--summary-->', summary))
    else:
        return ""


def send_email(html_template: Literal['email_template.html', 'youtube_api_error.html'], report_data: list):
    try:
        if not os.getenv('MAIL_USERNAME') or not os.getenv('MAIL_PASSWORD') or not os.getenv('MAIL_RECIPIENTS') or not os.getenv('MAIL_HOST') or not os.getenv('MAIL_PORT'):
            logger.error('Error: Missing email configuration')
        else:
            mail_username = os.getenv('MAIL_USERNAME') or ''
            mail_password = os.getenv('MAIL_PASSWORD') or ''
            mail_recipients = os.getenv('MAIL_RECIPIENTS') or ''
            mail_host = os.getenv('MAIL_HOST') or ''
            mail_port = int(os.getenv('MAIL_PORT') or '587')

            msg = MIMEMultipart('alternative')
            msg['From'] = mail_username
            msg['To'] = mail_recipients
            msg['Subject'] = 'Birdlife Youtube Livestream Report'
            template = load_email_template(html_template)
            if html_template == 'youtube_api_error.html':
                body = template
            else:
                body = generate_email_body(template, report_data)
            msg.attach(MIMEText(body, 'html'))
            with smtplib.SMTP(mail_host, mail_port) as server:
                server.starttls()
                server.login(mail_username, mail_password)
                server.send_message(msg)
            logger.info('Email sent successfully')
    except smtplib.SMTPException as e:
        logger.error(f"Error sending email: {e}")