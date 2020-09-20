#!/usr/bin/env python

import re
import json
import arrow

import scrape_common as sc


def parse_sh_date(date_str):
    return arrow.get(date_str, 'DD.MM.YYYY', locale='de').datetime.date()


def parse_sh_dates(content):
    res = re.search(r'\n(\d+\.\d+\.) - (\d+\.\d+\.)', content)
    if res is not None:
        year = '2020'
        end_date = parse_sh_date(res[2] + year)
        start_date = parse_sh_date(res[1] + year)
        return start_date, end_date
    return None, None


def get_categories(content):
    category_start = content.find('Kategorie')
    category_end = content.find('TOTAL')
    categories_str = content[category_start:category_end - 1]
    categories = categories_str.split('\n')
    return categories[1:]


def get_count(content):
    start = content.find('Anzahl')
    end = content.find('\n\n', start)
    count_str = content[start:end]
    count = count_str.split('\n')
    return count[1:]


def parse_sh_data(url, pdf):
    content = sc.pdf_to_text(pdf, page=10)

    start_date, end_date = parse_sh_dates(content)
    categories = get_categories(content)
    count = get_count(content)

    if len(categories) == len(count):
        for i in range(len(categories)):
            isd = sc.InfectionSourceData('SH', url)
            isd.source = categories[i]
            isd.count = count[i]
            isd.date_from = start_date.isoformat()
            isd.date_to = end_date.isoformat()
            print(isd)


def get_weekly_bulletin_url():
    base_url = 'https://sh.ch'
    url = base_url + '/CMS/content.jsp?contentid=6180531&language=DE&_=1600589165438'
    data = sc.download_json(url)
    data = json.loads(data['data_filemeta'])
    return base_url + data['url']


def scrape_sh():
    url = get_weekly_bulletin_url()
    # for now only parse the latest one
    pdf = sc.download_pdf(url)
    parse_sh_data(url, pdf)


if __name__ == '__main__':
    scrape_sh()
