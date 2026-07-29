from datetime import datetime
import logging

from fastapi import FastAPI
import dotenv

from email_report import send_email
from livestream_check import generate_livestream_status_report

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=f"logs/{datetime.now().strftime('%Y-%m-%d')}.log",
    )

dotenv.load_dotenv()

app = FastAPI()

@app.get('/report')
async def generate_report():
    report = await generate_livestream_status_report()
    send_email(report)
    return {
        "message": "Report generated and sent via email.",
        "data": [{ "name": stat.name, "url": stat.url, "status": stat.status } for stat in report]
    }
