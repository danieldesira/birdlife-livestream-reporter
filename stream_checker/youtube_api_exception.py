class YoutubeAPIException(Exception):

    def __init__(self, message: str):
        super().__init__(f"YouTube API Error: {message}")
