#!/usr/bin/env python

import re
import json
import arrow
from bs4 import BeautifulSoup

import scrape_common as sc


def parse_sh_date(date_str):
    return arrow.get(date_str, 'DD.MM.YYYY', locale='de').datetime.date()


def parse_sh_year(content):
    year = '2020'
    res = re.search(r'\d+\.\s+\w+\s+(\d{4})', content)
    if res:
        year = res[1]
    return year


def parse_sh_dates(content, year):
    res = re.search(r'\n(\d+\.\d+\.)\s?.\s?(\d+\.\d+\.)', content)
    if res is not None:
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
    # workaround for mixup with Anzahl and Prozentual values
    if count[1] == 'Prozentual':
        tmp = count
        count = []
        # also drop the last Total value
        for i in range(0, len(tmp) - 1, 2):
            count.append(tmp[i])
    return count[1:]


def parse_sh_data(url, pdf):
    found_data = False
    content = sc.pdf_to_text(pdf, page=1)
    year = parse_sh_year(content)
    for page in [11, 12, 13, 14, 15, 16, 17, 18]:
        content = sc.pdf_to_text(pdf, page=page)
        if re.match(r'.*Lage Schaffhausen . Ansteckungsorte.*', content):
            start_date, end_date = parse_sh_dates(content, year)
            categories = get_categories(content)
            count = get_count(content)

            if len(categories) == len(count):
                found_data = True
                for cat, cnt in zip(categories, count):
                    isd = sc.InfectionSourceData('SH', url)
                    isd.source = cat
                    isd.count = cnt
                    isd.date_from = start_date.isoformat()
                    isd.date_to = end_date.isoformat()
                    print(isd)

    assert found_data, f'No infection source data found in {url}!'


def get_weekly_bulletin_url():
    base_url = 'https://sh.ch'
    url = base_url + '/CMS/content.jsp?contentid=3209198&language=DE&_=1601060488274'
    data = sc.download_json(url)
    data = data['data_post_content']
    data = BeautifulSoup(data, 'html.parser').find('a', string=re.compile(r'Lagebericht aktuell'))
    data = data.get('contentid')
    url = base_url + f'/CMS/content.jsp?contentid={data}&language=DE'
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
