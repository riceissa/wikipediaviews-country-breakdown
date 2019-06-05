#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sys

from langmap import LANGMAP

def main():
    year_months = []
    year_months.append((2014, 12))
    for year in range(2015, 2018):
        for month in range(1, 13):
            if not (year == 2016 and month == 11):
                # SKIP 2016-11
                year_months.append((year, month))
    for month in range(1, 10):
        year_months.append((2018, month))

    url_pattern = "https://stats.wikimedia.org/archive/squid_reports/{}-{:02d}/SquidReportPageViewsPerCountryBreakdownHuge.htm"
    for year_month in year_months:
        year, month = year_month
        print("Doing year={}, month={:02d}".format(year, month), file=sys.stderr)
        url = url_pattern.format(year, month)

        response = requests.get(url)
        soup = BeautifulSoup(response.content, "lxml")

        # Use table index 2 if the report page is 2017-09 or older
        if year_month <= (2017, 9):
            table = soup.find_all("table")[2]
        else:
            table = soup.find_all("table")[1]
        country = None
        print("insert into viewcountsbymonth(pagename,`language`,drilldown,`monthfull`,viewcount) values")

        # We collect all the rows for a single page because sometimes we will
        # want to combine view counts for similar languages (e.g. counts for
        # zh-tw should be added to those of zh).
        rows_for_page = {}

        for row in table.find_all("tr")[4:]:
            if row.find("th").get("class") == ['lh3']:
                # This means we have started a new country section
                country = row.find("th").a.get("name")
            elif row.find("th").get("class") == ['l']:
                language = row.find("th").text
                if language in ["Other", "Portal", "m Wp", "Commons Wp", "wwwhttp Wp", "zero Wp", "plhttp Wp", "enhttp Wp", "eshttp Wp"]:
                    # Portal, m Wp, Commons Wp, wwwhttp Wp, zero Wp, and plhttp Wp
                    # all show up in 2015-04; I'm not really sure what's up with
                    # these.
                    # https://stats.wikimedia.org/archive/squid_reports/2015-04/SquidReportPageViewsPerCountryBreakdownHuge.htm
                    continue
                assert language.endswith(" Wp")
                lang_code = LANGMAP[language[:-len(" Wp")]]
                viewcount = row.find("td").text
                key = (country, lang_code, year, month)
                if key in rows_for_page:
                    rows_for_page[key] = rows_for_page[key] + int(viewcount + "000")
                else:
                    rows_for_page[key] = int(viewcount + "000")
            else:
                print("we don't know what this means", file=sys.stderr)
                raise ValueError

        first = True
        for (country, lang_code, year, month) in rows_for_page:
            print(("    " if first else "    ,") + "(" + ",".join([
                mysql_quote(country),
                mysql_quote(lang_code),
                mysql_quote("country-total"),
                mysql_quote("{}{:02d}".format(year, month)),
                str(rows_for_page[(country, lang_code, year, month)]),
            ]) + ")")
            first = False
        print(";\n")


def mysql_quote(x):
    """Quote the string x using MySQL quoting rules. If x is the empty string,
    return "NULL". Probably not safe against maliciously formed strings, but
    our input is fixed and from a basically trustable source."""
    if not x:
        return "NULL"
    x = x.replace("\\", "\\\\")
    x = x.replace("'", "''")
    x = x.replace("\n", "\\n")
    return "'{}'".format(x)



if __name__ == "__main__":
    main()
