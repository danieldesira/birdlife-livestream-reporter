from datetime import datetime
import logging
import os

import dotenv

from email_report import send_email
from livestream_check import generate_livestream_status_report

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=f"logs/{datetime.now().strftime('%Y-%m-%d')}.log",
    )

dotenv.load_dotenv()

if os.getenv('DEBUG', 'False') == 'True':
    import debugpy
    debugpy.listen(5678)
    print("Waiting for debugger to attach...")
    #debugpy.wait_for_client()
    print("Debugger attached...")

report = generate_livestream_status_report()
send_email(report)
