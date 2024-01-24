# pluginscraper.py - Python script in Selenium to Scrape ChatGPT for plugins on the app store
# Author: Evin Jaff

# Inspired by GPT-1984 (https://github.com/0ut0flin3/GPT-1984)
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
# Import chromedriver
from selenium.webdriver.chrome.options import Options
import pickle

import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
import sys
import time
import json
import shutil
import argparse
import requests
import sys
import config

parser = argparse.ArgumentParser(description="Crawl ChatGPT Plugin Store")
group = parser.add_mutually_exclusive_group()
group2 = parser.add_mutually_exclusive_group()
group3 = parser.add_mutually_exclusive_group()

group.add_argument("-u", "--unattended", help="Run in Unattended Mode",  action="store_true")
group.add_argument("-c", "--rebuild", help="Spawns Chrome and lets you re-make a dump of cookies",  action="store_true")

group2.add_argument("--existing-href", action="store_true")
# Group 3 is an override for the default behavior of using requests to get the openai urls
group3.add_argument("--use-selenium-for-openai-urls", action="store_true")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
def send_email(subject, body, to):
    msg = MIMEMultipart()
    msg['From'] = "evinjaffyt@gmail.com"
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(config.EMAIL_ADDRESS, config.EMAIL_SMTP_PASSWORD)
    # server.sendmail("evinjaffyt@gmail.com", to, text)
    server.quit()
    print("Email sent to " + to)
    return True

driver = None

def start_webdriver():
	global driver
	success = False
	for i in range(1, 10):
		try:
			driver = webdriver.Chrome()
			success = True
			break
		except Exception:
			traceback.print_exc()
			# if keyboard interrupt, exit
		if sys.exc_info()[0] == KeyboardInterrupt:
			sys.exit(1)
		
		print("Failed to start driver, trying again")
		time.sleep(1)
		continue

	if not success:
		print("Failed to start driver after 10 attempts")
		send_email("Error Occured Scraping Plugins", "Failed to start driver after 10 attempts", config.EMAIL_TO_SEND_ERROR_REPORT)
		sys.exit(1)

def scroll_to_bottom(driver):
    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)  # Wait for 1 second

def is_at_bottom(driver):
    # Check if the page is at the bottom
    return driver.execute_script("var scrollPosition = window.scrollY || window.pageYOffset || document.documentElement.scrollTop; var totalHeight = document.documentElement.scrollHeight;var visibleHeight = window.innerHeight;return scrollPosition + visibleHeight >= totalHeight - 10;")



def scrape_plugin_surf():
    driver.get('https://plugin.surf')
    # Feedback loop to scroll to the bottom
    try:
        while True:
            scroll_to_bottom(driver)
            time.sleep(2)
            if is_at_bottom(driver):
                # If at the bottom, you can break out of the loop or perform additional actions
                break
    except KeyboardInterrupt:
        # Handle interruption (e.g., user pressing Ctrl+C)
        pass

    print("Completed Scrolling to Bottom")

    elements = driver.find_elements(By.CLASS_NAME, "inline")

    # Create an empty list to store href values
    href_values = []

    # Iterate through the WebElement array and get href attributes
    for element in elements:
        href = element.get_attribute("href")
        href_values.append(href)

    # Verify the list of href values, remove any None values
    href_values = [x for x in href_values if x is not None]

    with open("href_values.json", "w") as outfile:
        json.dump(href_values, outfile)


    if args.use_selenium_for_openai_urls:
        print("Using Selenium to Get OpenAI URLS")
        print(f"{bcolors.WARNING}Warning: This is really slow. Only use if an automated request doesn't work{bcolors.ENDC}")
        dump_using_selenium(href_values)
    else:
        print("Using Requests to Get OpenAI URLS")
        # Verify that href_values.json exists
        if not os.path.exists("href_values.json"):
            print(f"{bcolors.WARNING}href_values.json does not exist. Waiting 5 seconds to in case the I/O needs to catch up{bcolors.WARNING}")
            time.sleep(5)

            if not os.path.exists("href_values.json"):
                print(f"{bcolors.FAIL}Error: href_values.json does not exist. {bcolors.ENDC}")
                sys.exit(1)
        
        gizmo_dict, failcodes = fetch_gizmos_from_href_file("href_values.json")

        # Now we can write this to a file
        with open("gizmos.json", "w") as outfile:
            json.dump(gizmo_dict, outfile)

        send_email("Successfully Scraped GPTs",  "Failed Requests:\n" + str(failcodes), config.EMAIL_TO_SEND_ERROR_REPORT)

    


def dump_using_selenium(href_values):
    for i in range(0, len(href_values)):
        print(href_values[i])

        driver.get(href_values[i])
        time.sleep(3)

            # For example, find all anchor elements using a locator strategy like XPath or CSS selector
        links = driver.find_elements(By.XPATH, "//a")

            # Create an empty list to store href values
        page_href_values = []

            # Iterate through the WebElement array and get href attributes
        for link in links:
            href = link.get_attribute("href")
            page_href_values.append(href)

            # only get the href values that are in the domain chat.openai.com
        page_href_values = [x for x in page_href_values if x is not None and "chat.openai.com" in x]

    with open("openai_href_values.json", "w") as outfile:
        json.dump(page_href_values, outfile)

    gizmo_array = []
    for page_href_value in page_href_values:
        specific_gizmo = fetch_openai_gizmo(page_href_value)
        gizmo_array.append(specific_gizmo)

        # Now that we have the gizmo array, we can write it to a file as a json, so we should also wrap it in a dictionary
    gizmo_dict = {"gizmos": gizmo_array}

        # Now we can write this to a file
    with open("gizmos.json", "w") as outfile:
        json.dump(gizmo_dict, outfile)


def fetch_openai_gizmo(openai_url):
     
     # Start by sanitizing the url, it should start with https://chat.openai.com/g/g-

    if not openai_url.startswith("https://chat.openai.com/g/g-"):
        # raise ValueError("Unknown OpenAI URL")
        return (None, False, "failed_valid_url")
    
    # the next sequence of characters up until the next hyphen is the gizmo id
    gizmo_id = openai_url[27:openai_url.find("-", 28)]

    # Once this is done, we can plug this into a request to the OpenAI API
    # This can be at https://chat.openai.com/backend-api/gizmos/<gizmo_id>

    headers = {
        "accept": "*/*",
        "accept-language": "en-US",
        "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "authorization": config.OPENAI_BEARER_TOKEN,
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }

    full_request_url = "https://chat.openai.com/backend-api/gizmos/g" + gizmo_id

    print(full_request_url)

    gizmo_request = requests.get(full_request_url, headers=headers )

    successful_request = True
    if gizmo_request.status_code != 200:
        # raise ValueError("Error Fetching Gizmo JSON @ URL " + full_request_url +  " Status Code: " + str(gizmo_request.status_code) + " " + gizmo_request.text)
        return (None, False, "bad_request")
    
    gizmo_json = None
    try:
        gizmo_json = gizmo_request.json()
    except:
        print("Error Fetching Gizmo JSON @ URL " + full_request_url +  " Status Code: " + str(gizmo_request.status_code))
        return (gizmo_json, False, "invalid_json")

    return (gizmo_json, successful_request, "none")

def fetch_gizmos_from_href_file(filename):
    with open(filename, "r") as infile:
        fail_logger = {
            "bad_request": 0,
            "failed_valid_url": 0,
            "invalid_json": 0
        }
        href_values = json.load(infile)

        gizmo_array = []

        for i in href_values:
            print(i)

            headers = {
                "accept": "*/*",
                "accept-language": "en-US",
                "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
                "sec-ch-ua-platform": "\"macOS\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin"
            }

            full_request_url = i

            request = requests.get(full_request_url, headers=headers )

            request_body = request.text

            # look for a url that starts with https://chat.openai.com/g/g-
            # find the string index that starts with https://chat.openai.com/g/g-
            # then find the next hyphen
            # the next sequence of characters up until the next hyphen is the gizmo id
            index_of_gizmo_id = request_body.find("https://chat.openai.com/g/g-")

            openai_url = request_body[index_of_gizmo_id:index_of_gizmo_id + 38]

            print(openai_url)

            specific_gizmo, success, reason = fetch_openai_gizmo(openai_url)

            if success:
                gizmo_array.append(specific_gizmo)
            else:
                fail_logger[reason] += 1

        # Now that we have the gizmo array, we can write it to a file as a json, so we should also wrap it in a dictionary
        gizmo_dict = {"gizmos": gizmo_array}

        return (gizmo_dict, fail_logger)

if __name__ == "__main__":
    args = parser.parse_args()
    
    if args.existing_href:
        print("Running in HREF Mode")
        fetch_gizmos_from_href_file("href_values.json")
        sys.exit(1)

    start_webdriver()
    if args.unattended:
        print("Running Unattended version")
    try:
        returned_json = scrape_plugin_surf()
    except:
        print(traceback.format_exc())
        send_email("Error Occured Scraping General Exception", traceback.format_exc(), config.EMAIL_TO_SEND_ERROR_REPORT)
    driver.quit()
