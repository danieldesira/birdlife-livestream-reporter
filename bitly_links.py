import requests

from custom_logger import setup_logger

logger = setup_logger()


def get_long_url(bitly_link: str):
    try:
        response = requests.get(bitly_link)
        return response.url
    except Exception:
        logger.error('Error getting long url')
