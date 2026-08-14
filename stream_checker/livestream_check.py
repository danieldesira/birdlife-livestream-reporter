from asyncio import sleep
import io
import json
import logging
import os
from typing import Literal
import imagehash
import imageio
import requests
from streamlink.session.session import Streamlink
from PIL import Image
from numpy import ndarray
from streamlink.stream.stream import Stream

from bitly_links import get_long_url
from report_stat import ReportStat
from stream_checker.youtube_api_exception import YoutubeAPIException

logger = logging.getLogger(__name__)


def get_youtube_live_id(youtube_url: str) -> str:
    return youtube_url.split('/')[-1].split('?')[0]


def get_api_stream_status(youtube_url: str):
    try:
        live_id = get_youtube_live_id(youtube_url)
        api_key = os.getenv('YOUTUBE_API_KEY')
        logger.info(f"Checking livestream status from Youtube API. Video ID: {live_id}")
        response = requests.get(f"https://www.googleapis.com/youtube/v3/videos?part=snippet,liveStreamingDetails&id={live_id}&key={api_key}")
        response_data = response.json()
        items = response_data.get('items')
        if not items:
            return ''
        snippet = items[0].get('snippet')
        if not snippet:
            return ''
        status = snippet.get('liveBroadcastContent', '')
        if response.status_code != 200:
            raise YoutubeAPIException(f"Error checking livestream status from Youtube API for {youtube_url}: {response.status_code} - {response.text}")
        logger.info(f"Stream status for {youtube_url}: {status}")
        return status
    except Exception as e:
        logger.error(f"Error checking livestream status from Youtube API for {youtube_url}: {e}")


def get_stream(youtube_url: str):
    sl = Streamlink()

    logger.info(f"Getting stream for URL: {youtube_url}")
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
    try:
        api_status = get_api_stream_status(youtube_url)
    except YoutubeAPIException as e:
        logger.error(f"Error checking API status for {youtube_url}: {e}")
        raise e

    logger.info(f"API status for {youtube_url}: {api_status}")

    if api_status != 'live':
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
        logger.error(f"Error validating stream {youtube_url}: {e}")
        return 'Offline'


def get_frame_hash(frame: ndarray):
    image = Image.frombytes(mode='RGBA', size=(1024, 1024), data=frame)
    return imagehash.phash(image)


async def generate_livestream_status_report():
    report = []
    streams = load_youtube_streams()
    if streams:
        for stream in streams:
            logger.info(f"Checking stream: {stream.get('name')}")
            try:
                youtube_url = get_long_url(stream.get('url')) or ''
                status = await validate_stream(youtube_url)
                report.append(ReportStat(stream.get('name'), stream.get('url'), status))

                logger.info(f"Stream status: {status}")
            except YoutubeAPIException as e:
                logger.error(f"Error checking stream {stream.get('name')}: {e} \nPlease check the YouTube API key and ensure it is valid.")
                raise e
            except Exception as e:
                logger.error(f"Error checking stream {stream.get('name')}: {e}")
    else:
        raise Exception("No streams found in youtube_streams.json")
    return report


def load_youtube_streams():
    if not os.path.exists('youtube_streams.json'):
        logger.error("youtube_streams.json file not found.")
        return None
    else:
        with open('youtube_streams.json') as file:
            return json.load(file)