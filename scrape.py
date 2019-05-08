#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sys

from langmap import LANGMAP

import pdb

def main():
    month = 201709
    url = "https://stats.wikimedia.org/archive/squid_reports/2014-11/SquidReportPageViewsPerCountryBreakdownHuge.htm"
    # SKIP 2016-11

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")

    # Use table index 2 if the report page is 2017-09 or older
    if month <= 201709:
        table = soup.find_all("table")[2]
    else:
        table = soup.find_all("table")[1]
    country = None
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
            print(country, lang_code, viewcount)
        else:
            print("we don't know what this means", file=sys.stderr)
            raise ValueError



if __name__ == "__main__":
    main()
