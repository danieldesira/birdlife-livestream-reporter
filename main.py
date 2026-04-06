from email_report import load_email_template
from livestream_check import generate_livestream_status_report

report = generate_livestream_status_report()

print(report)

print(load_email_template())