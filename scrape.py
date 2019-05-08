#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sys

from langmap import LANGMAP


def main():
    url = "https://stats.wikimedia.org/archive/squid_reports/2018-09/SquidReportPageViewsPerCountryBreakdownHuge.htm"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")

    table = soup.find_all("table")[1]
    country = None
    for row in table.find_all("tr")[4:]:
        if row.find("th").get("class") == ['lh3']:
            # This means we have started a new country section
            country = row.find("th").a.get("name")
        elif row.find("th").get("class") == ['l']:
            language = row.find("th").text
            if language == "Other":
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
