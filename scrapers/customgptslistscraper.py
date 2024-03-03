import sys
import time

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
# Import chromedriver
from selenium.webdriver.chrome.options import Options
import pickle

import traceback
import os
import time
import json
import shutil
import argparse
import requests
import config
import scraperutils
from scraperutils import bcolors


class CustomGPTsListScraper:
    ### Class Variables
    args = None
    driver = None
    ID = "customgptslistscraper"

    BACKUP_HREF_FILE_NAME = "../top_gpts_href_values_bak.json"
    BACKUP_OPENAI_URLS_FILE_NAME = "../top_gpts_openai_urls_bak.json"

    def scrape_all_gpts(self):
        self.driver.get('https://customgptslist.com/gpts')
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

        print("Completed Scrolling to Bottom")
        elements = self.driver.find_elements(By.TAG_NAME, "a")

        # Create an empty list to store href values
        href_values = []

        # Iterate through the WebElement array and get href attributes
        for element in elements:
            href = element.get_attribute("href")
            href_values.append(href)

        # Verify the list of href values, remove any None values
        href_values = [x for x in href_values if x is not None]

        with open(self.BACKUP_HREF_FILE_NAME, "w") as outfile:
            json.dump(href_values, outfile)

        return href_values


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
        subpage_urls = self.scrape_all_gpts()
        self.driver.quit()

        openai_urls = []
        for x in subpage_urls:
            openai_urls.append(scraperutils.extract_openai_url(x))

        num_failures = openai_urls.count(None)
        # Count the # of None values in openai_urls
        print(f"{bcolors.OKCYAN} Failures: {num_failures} {bcolors.ENDC}")

        openai_urls = [x for x in openai_urls if x is not None]

        print("Verifying uniqueness...")
        dupes = scraperutils.compute_duplicates(openai_urls)
        if len(dupes) > 0:
            print(f"{bcolors.WARNING}{len(dupes)} duplicates found{bcolors.ENDC}")
            print(dupes)

        # Remove duplicates from list
        openai_urls = list(set(openai_urls))

        with open(self.BACKUP_OPENAI_URLS_FILE_NAME, "w") as outfile:
            json.dump(openai_urls, outfile)

        return openai_urls

