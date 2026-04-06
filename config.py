import json


def load_youtube_streams():
    try:
        with open('youtube_streams.json') as file:
            return json.load(file)
    except FileNotFoundError:
        print('youtube_streams.json not found')
