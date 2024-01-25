
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


class AllGPTSScraper:
    ### Global Variables
    args = None
    driver = None
    ID = "pluginsurfscraper"

    BACKUP_HREF_FILE_NAME = "../plugin_surf_href_values_bak.json"
    BACKUP_OPENAI_URLS_FILE_NAME = "../plugin_surf_openai_urls_bak.json"

    def scrape_all_gpts(self):
        '''
        Gets a list of subpages from plugin.surf that may contain openAI urls
        :return:
        '''
        self.driver.get('https://allgpts.co/')

        Popup_button_xs = self.driver.find_element(By.ID, "closePopup")

        Popup_button_xs.click()

        time.sleep(1)

        # Show all GPTs
        self.driver.execute_script('showAll();this.hidden=true')

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
        # Run selenium to grab supages urls
        main_page_dump = self.scrape_all_gpts()
        self.driver.quit()

        openai_urls = scraperutils.bulk_extract_openai_url(main_page_dump)

        return openai_urls
