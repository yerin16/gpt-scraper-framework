# scraperutils.py
# Holds resuable functions for scraping so that the individual scraping scripts can stay clean
import sys
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import requests
import config
import smtplib
from selenium import webdriver
import traceback
import re

human_request_header = {
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


def extract_openai_url(openai_url):
    full_request_url = openai_url
    request = requests.get(full_request_url, headers=human_request_header)
    request_body = request.text

    # look for a url that starts with https://chat.openai.com/g/g-
    # find the string index that starts with https://chat.openai.com/g/g-
    # then find the next hyphen
    # the next sequence of characters up until the next hyphen is the gizmo id
    index_of_gizmo_id = request_body.find("chat.openai.com/g/g-")
    extracted_url = "https://" + request_body[index_of_gizmo_id:index_of_gizmo_id + 30]

    if index_of_gizmo_id == -1:
        print(f"{bcolors.WARNING}Failure to locate url, troubleshoot page: {openai_url} {bcolors.ENDC}")
        return None
    else:
        print(f"{bcolors.OKGREEN} {extracted_url} {bcolors.ENDC}")

    return extracted_url

# Webdriver JavaScript Macros
def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)  # Wait for 1 second

def scroll_jiggle(driver):
    iter_amount = random.randrange(4,13)

    for i in range(iter_amount):

        up_down = random.random()
        amt = random.randrange(100,500)
        direction = random.random() - .5

        commmand = "window.scrollBy(0,{});".format(int(amt*direction))
        driver.execute_script(commmand)

        delay = abs(random.random())

        time.sleep(delay)

def is_at_bottom(driver):
    # Check if the page is at the bottom
    return driver.execute_script("var scrollPosition = window.scrollY || window.pageYOffset || document.documentElement.scrollTop; var totalHeight = document.documentElement.scrollHeight;var visibleHeight = window.innerHeight;return scrollPosition + visibleHeight >= totalHeight - 10;")

def convert_openai_url_to_shortcode(openai_url):
    '''when given an openai url containing a gpt, convert it'''

    index_where_chat_starts = openai_url.find("chat.openai.com/g/g-")

    if index_where_chat_starts == -1:
        raise ValueError("Invalid openai url")

    # otherwise, we know where the
    index_where_code_starts = index_where_chat_starts+18
    length_of_shortcode = 10
    index_where_code_ends = index_where_code_starts + length_of_shortcode

    print(index_where_code_starts, length_of_shortcode)

    return openai_url[index_where_code_starts:index_where_code_ends]

def convert_short_code_to_openai_url(short_code):
    return "https://chat.openai.com/g/" + short_code + "-"





# Selenium Startup Code
def start_webdriver():
    success = False
    for i in range(1, 10):
        try:
            driver = webdriver.Chrome()
            success = True
            return driver
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
        send_email("Error Occured Scraping Plugins",
                   "Failed to start driver after 10 attempts",
                   config.EMAIL_TO_SEND_ERROR_REPORT)
        sys.exit(1)

#True Utility
def verify_unique(list) -> bool:
    '''
    Verifies that a list contains only unique elements
    :return:  True or False depending on whether the list contains only unique elements
    '''
    unique_elements = set(list)
    if len(unique_elements) > len(list):
        return False
    else:
        return True

def compute_duplicates(list) -> list:
    seen = set()
    dupes = []

    for x in list:
        if x in seen:
            dupes.append(x)
        else:
            seen.add(x)

    return dupes

# Logging and Email stuff
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
    msg['From'] = config.EMAIL_ADDRESS
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(config.EMAIL_ADDRESS, config.EMAIL_SMTP_PASSWORD)
    server.sendmail(config.EMAIL_ADDRESS, to, text)
    server.quit()
    print("Email sent to " + to)
    return True


def bulk_extract_openai_url(main_page_dump):
    '''
    Extracts OpenAI URLs given a page dump that contains urls that start with chat.openai.com
    :param main_page_dump:
    :return:
    '''
    urls = []
    url_pattern = r"chat\.openai\.com/g/g-\w+"

    for match in re.finditer(url_pattern, main_page_dump):
        url_start = match.start()
        extracted_url = "https://" + main_page_dump[url_start:url_start + 30]
        urls.append(extracted_url)

    if not urls:
        print(f"{bcolors.WARNING}Failure to locate any URLs {bcolors.ENDC}")
        return None
    else:
        for url in urls:
            print(f"{bcolors.OKGREEN} {url} {bcolors.ENDC}")

    return urls