# scraperutils.py
# Holds resuable functions for scraping so that the individual scraping scripts can stay clean
import sys
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import config
import smtplib
from selenium import webdriver
import traceback

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

def is_at_bottom(driver):
    # Check if the page is at the bottom
    return driver.execute_script("var scrollPosition = window.scrollY || window.pageYOffset || document.documentElement.scrollTop; var totalHeight = document.documentElement.scrollHeight;var visibleHeight = window.innerHeight;return scrollPosition + visibleHeight >= totalHeight - 10;")


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
    msg['From'] = "evinjaffyt@gmail.com"
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(config.EMAIL_ADDRESS, config.EMAIL_SMTP_PASSWORD)
    server.sendmail("evinjaffyt@gmail.com", to, text)
    server.quit()
    print("Email sent to " + to)
    return True