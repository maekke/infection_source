#!/usr/bin/env python

import xlrd

import scrape_common as sc


def scrape_ag():
    url = 'https://www.ag.ch/media/kanton_aargau/themen_1/coronavirus_1/daten_excel/Covid-19-Daten_Kanton_Aargau.xlsx'
    content = sc.download_content(url)
    xls = xlrd.open_workbook(file_contents=content)
    xls_datemode = xls.datemode
    sheet = xls.sheet_by_name('3. Ansteckungsorte')
    categories = {c: str(sheet.cell_value(1, c) or xlrd.formula.colname(c)) for c in range(1, sheet.ncols, 2)}
    for row in range(56, sheet.nrows):
        date = sheet.cell_value(row, 0)
        if date == '':
            return
        date = xlrd.xldate_as_datetime(date, xls_datemode).date()
        for col, cat in categories.items():
            # or should we use total count?
            count = sheet.cell_value(row, col)
            if count != '':
                count = int(count)
                isd = sc.InfectionSourceData('AG', url)
                isd.date = date.isoformat()
                isd.source = cat
                isd.count = str(count)
                print(isd)


if __name__ == '__main__':
    scrape_ag()
