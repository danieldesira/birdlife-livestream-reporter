from datetime import datetime
import logging

import asyncio
import dotenv

from email_report import send_email
from livestream_check import generate_livestream_status_report

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=f"logs/{datetime.now().strftime('%Y-%m-%d')}.log",
    )

dotenv.load_dotenv()

async def main():
    report = await generate_livestream_status_report()
    send_email(report)

if __name__ == "__main__":
    asyncio.run(main())