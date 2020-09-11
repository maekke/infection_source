#!/usr/bin/env python

import re
import datetime
import arrow
from bs4 import BeautifulSoup

import scrape_common as sc


def parse_vs_date(date_str):
    return arrow.get(date_str, 'DD.MM.YYYY', locale='fr').datetime.date()


def parse_vs_dates(pdf):
    content = sc.pdf_to_text(pdf, page=1)
    res = re.match(r'.* (\d+\.\d+) bis (\d+\.\d+\.20\d{2})', content, re.DOTALL)
    if res is not None:
        end_date = parse_vs_date(res[2])
        start_date = parse_vs_date(res[1] + '.' + str(end_date.year))
        return start_date, end_date
    return None, None


def strip_source(source):
    forbidden_words = ['sind', 'Personen', 'wurden', 'an ihrem', 'infiziert', '\.', 'die']
    for forbidden_word in forbidden_words:
        source = re.sub(r'(' + forbidden_word + ')', '', source)
    strip_chars = ['\n', '  ']
    for char in strip_chars:
        source = source.replace(char, ' ')
    source = source.strip()
    return source


def parse_vs_data(url, pdf):
    start_date, end_date = parse_vs_dates(pdf)

    content = sc.pdf_to_text(pdf, page=4)
    sources = {}
    for res in re.finditer(r'\s+(\d+) \([\d\.]+%\) ([\w\s\.]+)(;|\.)\n', content):
        sources[strip_source(res[2])] = int(res[1])
    for res in re.finditer(r'(\d+) (neue|neuer)?\s?(F.lle|F.llen|Fall beim Ausbruch),? \(?([\w\s]+)\s?(und|\.|;|\(|\))', content):
        sources[strip_source(res[4])] = int(res[1])

    for source, count in sources.items():
        isd = sc.InfectionSourceData('VS', url)
        isd.source = source
        isd.count = str(count or '')
        isd.date_from = start_date.isoformat()
        isd.date_to = end_date.isoformat()
        print(isd)


def get_weekly_bulletins():
    base_url = 'https://www.vs.ch'
    url = base_url + '/de/web/coronavirus/statistiques'
    content = sc.download(url)
    content = BeautifulSoup(content, 'html.parser')

    items = content.find_all(string=re.compile(r'Synthese.*Woche'))
    result = []
    for item in items:
        link = item.find_previous('a')
        result.append(base_url + link.attrs['href'])
    return result


def scrape_vs():
    bulletins = get_weekly_bulletins()
    # for now only parse the latest one
    pdf = sc.download_pdf(bulletins[0])
    parse_vs_data(bulletins[0], pdf)


if __name__ == '__main__':
    scrape_vs()
