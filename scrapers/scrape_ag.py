#!/usr/bin/env python

import re
import arrow
from bs4 import BeautifulSoup

import scrape_common as sc


def parse_date(date_str):
    return arrow.get(date_str, 'D. MMMM YYYY', locale='de_CH').datetime


def scrape_ag():
    url = 'https://www.ag.ch/de/themen_1/coronavirus_2/lagebulletins/lagebulletins_1.jsp'
    content = sc.download(url)
    content = BeautifulSoup(content, 'html.parser')

    subcat = content.find(string=re.compile('Verlauf Ansteckungsorte')).find_parent('h2').find_next('div')
    for category in subcat.findChildren('h2'):
        table_wrapper = category.find_next('div').findChild('div')
        table = table_wrapper.findChild('table')
        trs = table.findChildren('tr')
        n_trs = len(trs)
        assert n_trs > 0
        # skip header tr
        for i in range(1, n_trs):
            row = trs[i]
            tds = row.findChildren('td')
            isd = sc.InfectionSourceData('AG', url)
            isd.date = parse_date(tds[0].text).date().isoformat()
            isd.source = category.text
            isd.count = tds[2].text
            print(isd)


if __name__ == '__main__':
    scrape_ag()
