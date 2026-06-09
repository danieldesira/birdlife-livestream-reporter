from asyncio import sleep
import io
import json
from typing import Literal
import imagehash
import imageio
from streamlink.session.session import Streamlink
from PIL import Image
from numpy import ndarray
from streamlink.stream.stream import Stream
import logging

from bitly_links import get_long_url
from report_stat import ReportStat

logger = logging.getLogger(__name__)


def get_stream(youtube_url: str):
    sl = Streamlink()
    print(f"Getting stream for URL: {youtube_url}")
    streams = sl.streams(youtube_url)
    return streams['best']


def get_current_frame(stream: Stream):
    with stream.open() as fd:
        frame_bytes = fd.read(1024 * 1024)

    frame = imageio.v3.imread(io.BytesIO(frame_bytes), plugin='pyav')
    return frame


async def validate_stream(youtube_url: str) -> Literal['Online', 'Offline', 'Stalled']:
    logger.info(f"Validating stream: {youtube_url}")
    try:
        stream = get_stream(youtube_url)
        frame_hash_1 = get_frame_hash(get_current_frame(stream))
        logger.info(f"Frame 1 hash: {frame_hash_1}")
        await sleep(5)
        frame_hash_2 = get_frame_hash(get_current_frame(stream))
        logger.info(f"Frame 2 hash: {frame_hash_2}")
        logger.info(f"Frame difference: {frame_hash_2 - frame_hash_1}")
        if frame_hash_1 == frame_hash_2:
            logger.warning(f"Stream {youtube_url} appears to be stalled.")
            return 'Stalled'
        else:
            logger.info(f"Stream {youtube_url} is online.")
            return 'Online'
    except Exception as e:
        error_message = f"Error validating stream {youtube_url}: {e}"
        print(error_message)
        logger.error(error_message)
        return 'Offline'


def get_frame_hash(frame: ndarray):
    image = Image.frombytes(mode='RGBA', size=(1024, 1024), data=frame)
    return imagehash.phash(image)


async def generate_livestream_status_report():
    report = []
    streams = load_youtube_streams()
    if streams:
        for stream in streams:
            message = f"Checking stream: {stream.get('name')}"
            print(message)
            logger.info(message)
            try:
                youtube_url = get_long_url(stream.get('url')) or ''
                status = await validate_stream(youtube_url)
                report.append(ReportStat(stream.get('name'), stream.get('url'), status))

                message = f"Stream status: {status}"
                print(message)
                logger.info(message)
            except Exception as e:
                logger.error(f"Error checking stream {stream.get('name')}: {e}")
    return report


def load_youtube_streams():
    try:
        with open('youtube_streams.json') as file:
            return json.load(file)
    except FileNotFoundError:
        message = 'youtube_streams.json not found'
        print(message)
        logger.error(message)