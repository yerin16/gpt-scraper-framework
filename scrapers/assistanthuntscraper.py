
import sys
import time
from selenium.webdriver.common.by import By

import traceback

import os
import sys
import time
import json
import shutil
import argparse
import requests
import sys
import config
import scraperutils
from scraperutils import send_email
from scraperutils import bcolors
import re

class AssistantHuntScraper:
    ### Global Variables
    args = None
    driver = None
    ID = "assisatnthuntscraper"

    BACKUP_HREF_FILE_NAME = "../{}_href_values_bak.json".format(ID)
    BACKUP_OPENAI_URLS_FILE_NAME = "../{}_openai_urls_bak.json".format(ID)

    def dump_raw_html_from_url(self, url):
        self.driver.get(url)
        time.sleep(1)
        dumped_html_string = self.driver.page_source
        return dumped_html_string


    def get_category_page_urls(self):
        self.driver.get("https://assistanthunt.com/category")
        time.sleep(1)
        dumped_html_string = self.driver.page_source
        urls = []
        url_pattern = r"assistanthunt\.com\/category\/\w+"

        for match in re.finditer(url_pattern, dumped_html_string):
            url_start = match.start()
            extracted_url = "https://" + dumped_html_string[url_start:url_start + 30]
            urls.append(extracted_url)

        if not urls:
            print(f"{bcolors.WARNING}Failure to locate any URLs {bcolors.ENDC}")
            return None
        else:
            for url in urls:
                print(f"{bcolors.OKGREEN} {url} {bcolors.ENDC}")

        return urls
    def scrape(self, email_reporting=False) -> list:
        '''
        All scrapers must implement this method.
        It should return a list of OpenAI URLs corresponding to GPTs scraped
        from the class's web source. scrape() should also accept 3 mandatory kwargs
        but may also accept additional keyword arguments

        :param email_reporting: Whether it should send an email if there is a failure
        :return: List of strings that should be valid URLs
        '''
        self.driver = scraperutils.start_webdriver()
        # Run selenium to grab supages urls

        category_subpages = self.get_category_page_urls()
        print(category_subpages)

        for url in category_subpages:
            raw_page_dump = self.dump_raw_html_from_url(url)
            scraperutils.bulk_extract_openai_url(raw_page_dump)

        raise ValueError()



