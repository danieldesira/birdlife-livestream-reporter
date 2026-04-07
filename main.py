from email_report import send_email
from livestream_check import generate_livestream_status_report

report = generate_livestream_status_report()
send_email(report)
