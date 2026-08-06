from datetime import datetime
import logging

import asyncio
import dotenv

from email_report import send_email
from stream_checker.livestream_check import generate_livestream_status_report
from stream_checker.youtube_api_exception import YoutubeAPIException

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=f"logs/{datetime.now().strftime('%Y-%m-%d')}.log",
    )

dotenv.load_dotenv()

async def main():
    try:
        report = await generate_livestream_status_report()
        send_email('email_template.html', report)
    except YoutubeAPIException as e:
        send_email('youtube_api_error.html', [])
    except Exception as e:
        error_message = f"Error occurred while generating livestream status report: {e}"
        logging.error(error_message)
        print(error_message)

if __name__ == "__main__":
    asyncio.run(main())