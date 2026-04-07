from typing import Literal


class ReportStat:
    def __init__(self, name: str, url: str, status: Literal['Online', 'Offline']):
        self.__stream_name = name
        self.__stream_url = url
        self.__status = status

    @property
    def name(self):
        return self.__stream_name

    @property
    def url(self):
        return self.__stream_url

    @property
    def status(self):
        return self.__status
