#!/usr/bin/env python

import re
import sys
import arrow
from bs4 import BeautifulSoup

import scrape_common as sc


def parse_bs_date(date_str):
    return arrow.get(date_str, 'D. MMMM YYYY', locale='de_CH').datetime


def parse_number(number):
    # pylint: disable=R0911
    if number in ['ein', 'eine']:
        return 1
    if number == 'zwei':
        return 2
    if number == 'drei':
        return 3
    if number == 'vier':
        return 4
    if sc.match(r'(f.nf)', number):
        return 5
    if number == 'sechs':
        return 6
    if number == 'sieben':
        return 7
    if number == 'acht':
        return 8
    if number == 'neun':
        return 9
    return int(number)


def parse_source(source):
    forbidden_words = ['auf', 'an', 'in', 'der', 'w.hrend']
    for forbidden_word in forbidden_words:
        source = re.sub(r'(' + forbidden_word + ')', '', source)
    source = source.strip()
    return source


def parse_infection_sources(content):
    find_str = 'zugeordnet werden. '
    pos = content.find(find_str)
    if pos == -1:
        print('error could not detect infection sources', file=sys.stderr)
        return None
    pos += len(find_str)
    end_pos = content.find('. ', pos)
    if end_pos == -1:
        end_pos = content.rfind('.', pos)
    content = content[pos:end_pos]

    sources = content.split(', ')

    last = sources[-1].split(' und ')
    if len(last) != 2:
        print('error last source entry cannot be parsed properly', file=sys.stderr)
        return None
    sources[-1] = last[0]
    sources.append(last[1])

    result = []
    for source in sources:
        count = parse_number(sc.match(r'(\d+|[a-z]+)\s', source))
        res = re.match(r'.*(Prozent\))( der \d+ Neuinfektionen steckten sich)? (.*)', source)
        source = None
        if res is not None:
            source = parse_source(res[3])
        result.append((count, source))
    return result


def parse_weekly_bulletin(url):
    content = sc.download(url)
    content = BeautifulSoup(content, 'html.parser')
    content = content.find(string=re.compile('Im Zeitraum vom ')).find_parent('p').text
    # print(content)

    res = re.match(r'Im Zeitraum vom (\d.*20\d{2}) bis (\d.*20\d{2})', content)
    start_date = None
    if res is not None:
        start_date = parse_bs_date(res[1]).date()
        end_date = parse_bs_date(res[2]).date()
    assert start_date
    assert end_date

    total_infections = int(sc.match(r'.* wurden (\d+) Neuinfektionen', content))
    known_infections = int(sc.match(r'.* Dabei konnten.* \(oder (\d+) F.lle\)', content))
    unknown_infections = total_infections - known_infections

    infection_sources = parse_infection_sources(content)
    infection_sources.append((unknown_infections, 'Unbekannt'))

    for infection_source in infection_sources:
        isd = sc.InfectionSourceData('BS', url)
        isd.date_from = start_date.isoformat()
        isd.date_to = end_date.isoformat()
        isd.source = infection_source[1]
        isd.count = str(infection_source[0])
        print(isd)


def scrape_bs():
    base_url = 'https://www.coronavirus.bs.ch'
    content = sc.download(base_url)
    content = BeautifulSoup(content, 'html.parser')

    bulletin = content.find(string=re.compile('Coronavirus: Wochenbulletin')).find_parent('a')
    url = base_url + bulletin.get('href')
    parse_weekly_bulletin(url)


if __name__ == '__main__':
    scrape_bs()
