from email_report import generate_email_body
from livestream_check import generate_livestream_status_report

report = generate_livestream_status_report()
email_body = generate_email_body(report)

print('HTML report:')
print(email_body)