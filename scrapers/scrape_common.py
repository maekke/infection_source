#!/usr/bin/env python

import datetime
import re
import subprocess
import tempfile
import requests


class InfectionSourceData:
    # pylint: disable=too-many-instance-attributes

    __init_done = False
    SEPARATOR = ','

    def __init__(self, canton, url):
        assert canton
        assert url
        self.canton = canton
        self.url = url
        self.timestamp = datetime.datetime.utcnow()
        self.date = None
        self.time = None
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
        res.append(self.date or '')
        res.append(self.time or '')
        res.append(self.date_from or '')
        res.append(self.date_to or '')
        res.append(self.canton)
        res.append('"' + (self.source or '') + '"')
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
        res.append('time')
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


def match(regex, text, mode=None):
    if mode is None:
        res = re.match(regex, text)
    else:
        res = re.match(regex, text, mode)
    if res is not None:
        return res[1]
    return None


def download_pdf(url):
    req = requests.get(url)
    req.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(mode='wb', delete=False)
    tmp.write(req.content)
    tmp.close()
    return tmp.name


def pdf_to_text(path, layout=False, page=None):
    pdf_command = ['pdftotext', path, '-']
    if layout:
        pdf_command.append('-layout')
    if page:
        pdf_command.append('-f')
        pdf_command.append(str(page))
        pdf_command.append('-l')
        pdf_command.append(str(page))
    with subprocess.Popen(pdf_command, stdout=subprocess.PIPE) as text:
        out = text.stdout.read()
        text.wait()
        return out.decode('utf-8')
