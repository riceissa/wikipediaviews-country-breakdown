#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sys

from langmap import LANGMAP

import pdb

def main():
    month = 201709
    url = "https://stats.wikimedia.org/archive/squid_reports/2015-04/SquidReportPageViewsPerCountryBreakdownHuge.htm"
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
            if language == "Other" or language == "Portal" or language == "m Wp" or language == "Commons Wp" or language == "wwwhttp Wp" or language == "zero Wp" or language == "plhttp Wp":
                # The portal thing shows up in https://stats.wikimedia.org/archive/squid_reports/2015-04/SquidReportPageViewsPerCountryBreakdownHuge.htm
                # I'm not sure what "m Wp" means; maybe mobile?
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
