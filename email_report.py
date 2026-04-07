import smtplib
from email.message import EmailMessage


def load_email_template():
    try:
        with open('email_template.html') as file:
            return file.read()
    except FileNotFoundError:
        print('email_template.html not found')


def generate_email_body(report_data: list):
    template = load_email_template()
    table_markup = ''.join(map(lambda stat: f"<tr><td>{stat.name}</td><td>{stat.status}</td></tr>", report_data))
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
        msg = EmailMessage()
        msg['From'] = 'info@birdlifemalta.org'
        msg['To'] = 'desiradaniel2007@gmail.com'
        msg['Subject'] = 'Birdlife Youtube Livestream Report'
        msg['Body'] = generate_email_body(report_data).replace('\n', '').replace('\r', '')
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login('', '')
        server.send_message(msg)
    except smtplib.SMTPException:
        print('Error: unable to send email')
