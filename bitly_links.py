import requests


def get_long_url(bitly_link: str):
    try:
        response = requests.get(bitly_link)
        return response.url
    except Exception:
        print('Error getting long url')
