import json
from selenium.webdriver.common.by import By
import scraperutils
import time

class MeetGPTsScraper:
    ### Global Variables
    args = None
    driver = None
    ID = "meetgpts"

    BACKUP_HREF_FILE_NAME = "../tiny_href_values_bak.json"
    BACKUP_OPENAI_URLS_FILE_NAME = "../tiny_openai_urls_bak.json"


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

        self.driver.get("https://meetgpts.com/")

        time.sleep(1)
        dumped_html_string = self.driver.page_source

        self.driver.quit()

        openai_urls = scraperutils.bulk_extract_openai_url(dumped_html_string)
        return openai_urls