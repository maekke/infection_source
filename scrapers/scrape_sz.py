#!/usr/bin/env python

import re
import datetime
import arrow

import scrape_common as sc


def parse_sz_date(date_str):
    return arrow.get(date_str, 'DD. MMMM YYYY', locale='de_CH').datetime.date()


def parse_sz_dates(content):
    # den Zeitraum vom 16. Juli bis 19. August 2020
    res = re.match(r'.*\nTabelle:.*vom (\d+. \w+) bis (\d+. \w+ 20\d{2})', content, re.DOTALL)
    if res is not None:
        start_date = parse_sz_date(res[1] + ' 2020')
        end_date = parse_sz_date(res[2])
        start_date = datetime.date(end_date.year, start_date.month, start_date.day)
        return start_date, end_date
    return None, None


def strip_sz_source(source):
    source = source.strip()
    return source.replace('*', '')


def parse_sz_data(url, pdf):
    content = sc.pdf_to_text(pdf, page=3, layout=True)
    date_from, date_to = parse_sz_dates(content)

    sources = {}
    start_str = 'Prozentualer Anteil'
    start_pos = content.find(start_str) + len(start_str)
    end_pos = content.find('\n Total')
    content = content[start_pos:end_pos]
    for line in content.split('\n'):
        res = re.match(r'^\s(.*)\s\s(\d+)\s+(\d+\.\d{2})$', line)
        if res is not None:
            sources[strip_sz_source(res[1])] = int(res[2])

    for source, count in sources.items():
        isd = sc.InfectionSourceData('SZ', url)
        isd.source = source
        isd.count = str(count)
        isd.date_from = date_from.isoformat()
        isd.date_to = date_to.isoformat()
        print(isd)


def scrape_sz():
    url = 'https://www.sz.ch/public/upload/assets/48367/KA_27_20_Antwort_BAG_Zahlen.pdf'
    pdf = sc.download_pdf(url)
    parse_sz_data(url, pdf)


if __name__ == '__main__':
    scrape_sz()
