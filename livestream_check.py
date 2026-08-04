from asyncio import sleep
from http.cookiejar import MozillaCookieJar
import io
import json
import os
from typing import Literal
import imagehash
import imageio
import requests
from streamlink.session.session import Streamlink
from PIL import Image
from numpy import ndarray
from streamlink.stream.stream import Stream
import logging

from bitly_links import get_long_url
from report_stat import ReportStat

logger = logging.getLogger(__name__)


def get_youtube_live_id(youtube_url: str) -> str:
    return youtube_url.split('/')[-1].split('?')[0]


def get_api_stream_status(youtube_url: str):
    live_id = get_youtube_live_id(youtube_url)
    api_key = os.getenv('YOUTUBE_API_KEY')
    logger.info(f"Checking livestream status from Youtube API. Video ID: {live_id}")
    try:
        response = requests.get(f"https://www.googleapis.com/youtube/v3/videos?part=snippet,liveStreamingDetails&id={live_id}&key={api_key}")
        status = response.json().get('items', [{}])[0].get('snippet', {}).get('liveBroadcastContent', 'Offline')
        logger.info(f"Stream status for {youtube_url}: {status}")
        if status == 'live':
            return 'Online'
        else:
            return 'Offline'
    except Exception as e:
        logger.error(f"Error checking livestream status from Youtube API for {youtube_url}: {e}")
        return 'Offline'


def get_stream(youtube_url: str):
    sl = Streamlink()

    print(f"Getting stream for URL: {youtube_url}")
    streams = sl.streams(youtube_url)
    logger.info(f"Available streams for {youtube_url}: {list(streams.keys())}")
    if not streams:
        logger.warning(f"No streams extracted for {youtube_url} — likely blocked or extraction failure")
    return streams['best']


def get_current_frame(stream: Stream):
    with stream.open() as fd:
        frame_bytes = fd.read(1024 * 1024)

    frame = imageio.v3.imread(io.BytesIO(frame_bytes), plugin='pyav')
    return frame


async def validate_stream(youtube_url: str) -> Literal['Online', 'Offline', 'Stalled']:
    logger.info(f"Validating stream: {youtube_url}")
    api_status = get_api_stream_status(youtube_url)

    logger.info(f"API status for {youtube_url}: {api_status}")

    if api_status == 'Offline':
        return 'Offline'
    
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
    else:
        raise Exception("No streams found in youtube_streams.json")
    return report


def load_youtube_streams():
    if not os.path.exists('youtube_streams.json'):
        logger.error("youtube_streams.json file not found.")
        print("youtube_streams.json file not found.")
        return None
    else:
        with open('youtube_streams.json') as file:
            return json.load(file)