from asyncio import sleep
import io
import json
import imagehash
import imageio
import streamlink
from PIL import Image
from numpy import ndarray
from streamlink.stream.hls import HLSStream
import logging

from bitly_links import get_long_url
from report_stat import ReportStat

logger = logging.getLogger(__name__)


def get_stream(youtube_url: str):
    sl = streamlink.Streamlink()
    print(f"Getting stream for URL: {youtube_url}")
    streams = sl.streams(youtube_url)
    return streams['best']


def get_current_frame(stream: HLSStream):
    with stream.open() as fd:
        frame_bytes = fd.read(1024 * 1024)

    frame = imageio.v3.imread(io.BytesIO(frame_bytes), plugin='pyav')
    return frame


async def validate_stream(youtube_url: str):
    logger.info(f"Validating stream: {youtube_url}")
    try:
        stream = get_stream(youtube_url)
        print(stream.url)
        frame_hash_1 = get_frame_hash(get_current_frame(stream))
        await sleep(1)
        frame_hash_2 = get_frame_hash(get_current_frame(stream))
        print(f"Frame hash 1: {frame_hash_1}, Frame hash 2: {frame_hash_2}")
        return frame_hash_1 != frame_hash_2
    except Exception as e:
        error_message = f"Error validating stream {youtube_url}: {e}"
        print(error_message)
        logger.error(error_message)
        return False


def get_frame_hash(frame: ndarray):
    image = Image.frombytes(mode='RGBA', size=(1024, 1024), data=frame)
    return imagehash.phash(image)


async def generate_livestream_status_report():
    report = []
    streams = load_youtube_streams()
    if streams:
        for stream in streams:
            print(f"Checking stream: {stream.get('name')}")
            logger.info(f"Checking stream: {stream.get('name')}")
            try:
                youtube_url = get_long_url(stream.get('url')) or ''
                if await validate_stream(youtube_url):
                    status = 'Online'
                else:
                    status = 'Offline'
                report.append(ReportStat(stream.get('name'), stream.get('url'), status))
                print(f"Stream status: {status}")
                logger.info(f"Stream status: {status}")
            except Exception as e:
                logger.error(f"Error checking stream {stream.get('name')}: {e}")
    return report


def load_youtube_streams():
    try:
        with open('youtube_streams.json') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error('youtube_streams.json not found')