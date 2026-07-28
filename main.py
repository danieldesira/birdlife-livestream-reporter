from datetime import datetime
import logging

import dotenv
from fastapi import FastAPI

from email_report import send_email
from livestream_check import generate_livestream_status_report
import asyncio

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
    return {"message": "Report generated and sent via email.", "html": report}
