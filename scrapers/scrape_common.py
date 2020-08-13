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
        if self.date is not None:
            res.append(self.date.isoformat())
        else:
            res.append('')
        res.append(self.date_from or '')
        res.append(self.date_to or '')
        res.append(self.canton)
        res.append(self.source or '')
        res.append(self.count or '')
        res.append(self.url)
        return InfectionSourceData.SEPARATOR.join(res)

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
