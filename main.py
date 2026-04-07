import dotenv

from email_report import send_email
from livestream_check import generate_livestream_status_report

dotenv.load_dotenv()

report = generate_livestream_status_report()
send_email(report)
