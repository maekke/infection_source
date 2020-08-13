#!/usr/bin/env python

import csv
from io import StringIO
import re
import datetime

import scrape_common as sc


def parse_date(date_str):
    return datetime.datetime.strptime(date_str, '%d.%m.%Y %H:%M')


data = []
date = None

url = 'https://www.zg.ch/behoerden/gesundheitsdirektion/statistikfachstelle/daten/themen/result-themen-14-03-05.csv'
content = sc.download(url)
reader = csv.DictReader(StringIO(content), delimiter=',')
for row in reader:
    source = row['Ansteckungsquelle']
    if source != 'NA':
        isd = sc.InfectionSourceData('ZG', url)
        isd.source = source
        isd.count = row['Anzahl']
        data.append(isd)

    if row['Type'] == 'subtitle':
        content = row['Content']
        res = re.search('Datenstand: (.*)$', content)
        if res:
            date = parse_date(res[1])

assert date is not None
print(sc.InfectionSourceData.header())
for item in data:
    item.date = date
    print(item)
