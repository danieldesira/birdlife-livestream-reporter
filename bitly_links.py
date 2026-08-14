import logging

import requests

logger = logging.getLogger(__name__)


def get_long_url(bitly_link: str):
    try:
        response = requests.get(bitly_link)
        return response.url
    except Exception as e:
        logger.error(f'Error getting long url: {bitly_link} {e}')
