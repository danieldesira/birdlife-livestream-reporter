import io

import imagehash
import imageio
import streamlink
from PIL import Image
from av.stream import Stream

from config import load_youtube_streams
from report_stat import ReportStat


def get_stream(youtube_url: str):
    sl = streamlink.Streamlink()
    streams = sl.streams(youtube_url)
    return streams['best']


def get_current_frame(stream: Stream):
    with stream.open() as fd:
        frame_bytes = fd.read(1024 * 1024)

    frame = imageio.v3.imread(io.BytesIO(frame_bytes), plugin='pyav')
    return frame


def validate_stream(youtube_url: str):
    try:
        stream = get_stream(youtube_url)
        last_frame_hash = get_frame_hash(get_current_frame(stream))
        differences = []
        for i in range(0, 4):
            frame_hash = get_frame_hash(get_current_frame(stream))
            differences.append(frame_hash - last_frame_hash)
            last_frame_hash = frame_hash
        return any(x > 5 for x in differences)

    except Exception as e:
        print(e)
        return False


def get_frame_hash(frame):
    image = Image.frombytes(mode='RGBA', size=(1024, 1024), data=frame)
    return imagehash.phash(image)


def generate_livestream_status_report():
    report = []
    for stream in load_youtube_streams():
        print('Checking', stream.get('name'))
        try:
            is_online = validate_stream(stream.get('url'))
            if is_online:
                status = 'Online'
            else:
                status = 'Offline'
            report.append(ReportStat(stream.get('name'), stream.get('url'), status))
            print('Online:', is_online)
        except Exception as e:
            print(e)
    return report
