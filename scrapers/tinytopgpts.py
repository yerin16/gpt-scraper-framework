import json
from selenium.webdriver.common.by import By
import scraperutils
import time

class TinyTopGPTS:
    ### Global Variables
    args = None
    driver = None
    ID = "tinytopgtps"
    LIMIT = 20

    BACKUP_HREF_FILE_NAME = "../tiny_href_values_bak.json"
    BACKUP_OPENAI_URLS_FILE_NAME = "../tiny_openai_urls_bak.json"

    def scrape_top_gpts(self):
        self.driver.get('https://www.topgpts.ai/')

        elements = self.driver.find_elements(By.TAG_NAME, "a")
        time.sleep(5)
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
        subpage_urls = self.scrape_top_gpts()
        self.driver.quit()

        # Limit the amount of urls
        subpage_urls = subpage_urls[:self.LIMIT]

        openai_urls = []
        for x in subpage_urls:
            openai_urls.append(scraperutils.extract_openai_url(x))

        num_failures = openai_urls.count(None)
        # Count the # of None values in openai_urls
        print(f"{scraperutils.bcolors.OKCYAN} Failures: {num_failures} {scraperutils.bcolors.ENDC}")

        openai_urls = [x for x in openai_urls if x is not None]

        print("Verifying uniqueness...")
        dupes = scraperutils.compute_duplicates(openai_urls)
        if len(dupes) > 0:
            print(f"{scraperutils.bcolors.WARNING}{len(dupes)} duplicates found{scraperutils.bcolors.ENDC}")
            print(dupes)

        # Remove duplicates from list
        openai_urls = list(set(openai_urls))

        with open(self.BACKUP_OPENAI_URLS_FILE_NAME, "w") as outfile:
            json.dump(openai_urls, outfile)

        return openai_urls

