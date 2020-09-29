#!/usr/bin/env python

import re
import arrow
from bs4 import BeautifulSoup

import scrape_common as sc


def parse_ag_date(date_str):
    return arrow.get(date_str, 'DD.MM.YYYY', locale='de_CH').datetime


def scrape_ag():
    url = 'https://www.ag.ch/de/themen_1/coronavirus_2/lagebulletins/lagebulletins_1.jsp'
    content = sc.download(url)
    content = BeautifulSoup(content, 'html.parser')

    # get the date from the last row
    table = content.find(string=re.compile('1. Daten zu Covid-19')).find_next('table')
    rows = table.findChildren('tr')
    tds = rows[-1].findChildren('td')
    date = parse_ag_date(tds[0].text).date().isoformat()

    # get the data
    table = content.find(string=re.compile('ANSTECKUNGSORT')).find_parent('table')
    trs = table.findChildren('tr')
    n_trs = len(trs)
    assert n_trs > 0
    # skip header and total in tr
    for i in range(1, n_trs - 1):
        row = trs[i]
        tds = row.findChildren('td')
        isd = sc.InfectionSourceData('AG', url)
        isd.date = date
        isd.source = tds[0].text
        isd.count = tds[1].text
        print(isd)


if __name__ == '__main__':
    scrape_ag()
