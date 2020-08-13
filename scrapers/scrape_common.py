#!/usr/bin/env python

import datetime
import requests


class InfectionSourceData:
    __init_done = False
    SEPARATOR = ','

    def __init__(self, canton, url):
        assert canton
        assert url
        self.canton = canton
        self.url = url
        self.timestamp = datetime.datetime.utcnow()
        self.date = None
        self.date_from = None
        self.date_to = None
        self.source = None
        self.count = None

        self.__init_done = True

    def __setattr__(self, key, value):
        if self.__init_done and not hasattr(self, key):
            raise TypeError('unknown key: {0}'.format(key))
        object.__setattr__(self, key, value)

    def __str__(self):
        res = []
        res.append(self.__get_date(self.date))
        res.append(self.__get_date(self.date_from))
        res.append(self.__get_date(self.date_to))
        res.append(self.canton)
        res.append(self.source or '')
        res.append(self.count or '')
        res.append(self.url)
        return InfectionSourceData.SEPARATOR.join(res)

    @staticmethod
    def __get_date(date):
        if date is not None:
            return date.isoformat()
        return ''

    @staticmethod
    def header():
        res = []
        res.append('date')
        res.append('date_from')
        res.append('date_to')
        res.append('canton')
        res.append('source')
        res.append('count')
        res.append('url')
        return InfectionSourceData.SEPARATOR.join(res)


def download(url, encoding='utf-8'):
    req = requests.get(url)
    req.raise_for_status()
    if encoding:
        req.encoding = encoding
    return req.text