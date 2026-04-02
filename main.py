from livestream_check import validate_stream

youtube_streams = [
    {'name': 'Zurrieq Primary', 'url': 'https://www.youtube.com/live/VEsYJTU2Euw'},
    {'name': 'San Anton Gardens', 'url': 'https://www.youtube.com/live/V5s60c562xM'},
    {'name': 'Salina Saltpans', 'url': 'https://www.youtube.com/live/fsD686C6ueI'},
    {'name': 'Stella Maris', 'url': 'https://www.youtube.com/live/eanzIJ5oRcc'},
    {'name': 'Villa Messina', 'url': 'https://www.youtube.com/live/UlwqS7xSICk'}
]

for stream in youtube_streams:
    print(stream.get('name'))
    try:
        frame = validate_stream(stream.get('url'))
        print(frame)
    except Exception as e:
        print(e)
