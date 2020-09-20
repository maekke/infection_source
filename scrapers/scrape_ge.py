#!/usr/bin/env python

import datetime
import re
import tempfile
import subprocess
import arrow

import scrape_common as sc


def parse_diagram(pdf):
    with tempfile.TemporaryDirectory() as tmpdirname:
        pdf_command = ['pdfimages', '-png', '-f', '6', '-l', '6', pdf, tmpdirname + '/']
        with subprocess.Popen(pdf_command) as pdf_proc:
            pdf_proc.wait()
            tesseract_command = ['tesseract', tmpdirname + '/-002.png', 'stdout']
            with subprocess.Popen(tesseract_command, stdout=subprocess.PIPE) as text:
                out = text.stdout.read()
                text.wait()
                return out.decode('utf-8')


def get_categories_from_diagram(pdf):
    content = parse_diagram(pdf)
    categories = []
    values = []
    for item in content.split('\n'):
        res = re.match(r'^.(.)? (.+)$', item)
        if res is not None:
            categories.append(res[2])
        res = re.match(r'^(\d+)$', item)
        if res is not None:
            values.append(int(res[1]))
    # ignore 90, 80, ... 10 values
    try:
        idx = values.index(10)
        if idx >= 0:
            values = values[idx + 1:]
    except ValueError:
        pass

    result = {}
    # Autre seems to be the largest number and at values index 1
    try:
        idx = categories.index('Autre')
        if idx >= 0:
            result['Autre'] = values[1]
            categories.pop(idx)
            values.pop(1)
    except ValueError:
        pass

    for category, value in zip(categories, values):
        value = value
        result[category] = value
    return result


def parse_ge_date(date_str):
    return arrow.get(date_str, 'D MMMM YYYY', locale='fr').datetime.date()


def parse_dates(content):
    res = re.search(r'\n(\d+|\d+ .*) au (\d+ .* 20\d{2})', content)
    if res is not None:
        end_date = parse_ge_date(res[2])
        if len(res[1]) <= 2:
            start_date = datetime.date(end_date.year, end_date.month, int(res[1]))
        else:
            start_date = parse_ge_date(res[1] + ' ' + str(end_date.year))
        return start_date, end_date
    return None, None


def parse_data(url, pdf, content):
    start_date, end_date = parse_dates(content)
    categories = get_categories_from_diagram(pdf)
    for category, count in categories.items():
        isd = sc.InfectionSourceData('GE', url)
        isd.source = category
        isd.count = str(count or '')
        isd.date_from = start_date.isoformat()
        isd.date_to = end_date.isoformat()
        print(isd)


def scrape_ge():
    url = 'https://www.ge.ch/document/19696/telecharger'
    pdf = sc.download_pdf(url)
    content = sc.pdf_to_text(pdf)
    parse_data(url, pdf, content)


if __name__ == '__main__':
    scrape_ge()
