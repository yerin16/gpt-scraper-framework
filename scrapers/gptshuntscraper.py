
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


class GPTsHuntScraper:
    ### Global Variables
    args = None
    driver = None
    ID = "gptshuntscraper"

    BACKUP_HREF_FILE_NAME = "../{}_href_values_bak.json".format(ID)
    BACKUP_OPENAI_URLS_FILE_NAME = "../{}_openai_urls_bak.json".format(ID)

    def scrape_all_gpts(self):
        '''
        Gets a list of subpages from plugin.surf that may contain openAI urls
        :return:
        '''
        self.driver.get('https://www.gptshunt.tech/hunt')

        # Feedback loop to scroll to the bottom
        try:
            while True:
                scraperutils.scroll_to_bottom(self.driver)
                time.sleep(2)
                if scraperutils.is_at_bottom(self.driver):
                    # If at the bottom, you can break out of the loop or perform additional actions
                    break
        except KeyboardInterrupt:
            # Handle interruption (e.g., user pressing Ctrl+C)
            pass

        time.sleep(1)
        dumped_html_string = self.driver.page_source
        return dumped_html_string

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
        main_page_dump = self.scrape_all_gpts()
        self.driver.quit()

        openai_urls = scraperutils.bulk_extract_openai_url(main_page_dump)

        return openai_urls
