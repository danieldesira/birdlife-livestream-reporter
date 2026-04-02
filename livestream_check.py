import io

import imagehash
import imageio
import streamlink
from PIL import Image
from av.stream import Stream


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
        for i in range(0, 4):
            frame_hash = get_frame_hash(get_current_frame(stream))
        print(frame_hash - last_frame_hash)

    except Exception as e:
        print(e)
        return False


def get_frame_hash(frame: list):
    image = Image.fromarray(frame)
    return imagehash.phash(image)

