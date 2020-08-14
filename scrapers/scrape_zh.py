#!/usr/bin/env python

import csv
from io import StringIO
import datetime

import scrape_common as sc


def parse_date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date().isoformat()


URL = 'https://raw.githubusercontent.com/openZH/covid_19_contact_tracing_ZH/master/data/Ansteckungswege.csv'
content = sc.download(URL)
reader = csv.DictReader(StringIO(content), delimiter=',')
for row in reader:
    isd = sc.InfectionSourceData('ZH', URL)
    isd.date_from = parse_date(row['from'])
    isd.date_to = parse_date(row['until'])
    isd.source = row['context_cat']
    if isd.source == '':
        isd.source = row['context_bool']
    isd.count = row['n_conf']
    print(isd)
