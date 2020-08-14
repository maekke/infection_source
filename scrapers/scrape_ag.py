#!/usr/bin/env python

from bs4 import BeautifulSoup
import re
import datetime

import scrape_common as sc


def parse_date(date_str):
    # TODO improve this..
    date_str = date_str.split(',')[1]
    date_str = date_str.strip()
    date_str = date_str.replace('Juli', '07.')
    date_str = date_str.replace('August', '08.')
    return datetime.datetime.strptime(date_str, '%d. %m. %Y')


url = 'https://www.ag.ch/de/themen_1/coronavirus_2/lagebulletins/lagebulletins_1.jsp'
content = sc.download(url)

soup = BeautifulSoup(content, 'html.parser')

h2 = soup.find(string=re.compile('Verlauf Ansteckungsorte')).find_parent('h2')

subcat = h2.find_next('div')
categories = subcat.findChildren('h2')
print(sc.InfectionSourceData.header())
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
        isd = sc.InfectionSourceData('AG', url)
        isd.date = parse_date(tds[0].text).date().isoformat()
        isd.source = cat
        isd.count = tds[2].text
        print(isd)
