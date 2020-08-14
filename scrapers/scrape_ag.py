#!/usr/bin/env python

import re
import arrow
from bs4 import BeautifulSoup

import scrape_common as sc


def parse_date(date_str):
    return arrow.get(date_str, 'D. MMMM YYYY', locale='de_CH').datetime


URL = 'https://www.ag.ch/de/themen_1/coronavirus_2/lagebulletins/lagebulletins_1.jsp'
content = sc.download(URL)

soup = BeautifulSoup(content, 'html.parser')

h2 = soup.find(string=re.compile('Verlauf Ansteckungsorte')).find_parent('h2')

subcat = h2.find_next('div')
categories = subcat.findChildren('h2')
for category in categories:
    cat = category.text
    accordion = category.find_next('div')
    table_wrapper = accordion.findChild('div')
    table = table_wrapper.findChild('table')
    trs = table.findChildren('tr')
    n = len(trs)
    assert n > 0
    # skip header tr
    for i in range(1, n):
        tr = trs[i]
        tds = tr.findChildren('td')
        isd = sc.InfectionSourceData('AG', URL)
        isd.date = parse_date(tds[0].text).date().isoformat()
        isd.source = cat
        isd.count = tds[2].text
        print(isd)
