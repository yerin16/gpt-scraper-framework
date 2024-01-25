# metascraper.py - Call the other scrapers to grab OpenAI URLs
# This script puts it all together- takes the universal interface of OpenAI URLS, calls OpenAI
# And generates JSONS of them
import argparse
import json
import requests
import config

from pick import pick

import scraperutils
from topgptsscraper import TopGPTsScraper


# if args.use_selenium_for_openai_urls:
#     print("Using Selenium to Get OpenAI URLS")
#     print(f"{bcolors.WARNING}Warning: This is really slow. Only use if an automated request doesn't work{bcolors.ENDC}")
#     dump_using_selenium(href_values)
# else:
#     print("Using Requests to Get OpenAI URLS")
#     # Verify that href_values.json exists
#     if not os.path.exists("href_values.json"):
#         print \
#             (f"{bcolors.WARNING}href_values.json does not exist. Waiting 5 seconds to in case the I/O needs to catch up{bcolors.WARNING}")
#         time.sleep(5)
#
#         if not os.path.exists("href_values.json"):
#             print(f"{bcolors.FAIL}Error: href_values.json does not exist. {bcolors.ENDC}")
#             sys.exit(1)
#
#     gizmo_dict, failcodes = fetch_gizmos_from_href_file("href_values.json")
#
#     # Now we can write this to a file
#     with open("gizmos.json", "w") as outfile:
#         json.dump(gizmo_dict, outfile)
#
#     send_email("Successfully Scraped GPTs",  "Failed Requests:\n" + str(failcodes), config.EMAIL_TO_SEND_ERROR_REPORT)

# Methods for Dumping URLS
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

    gizmo_request = requests.get(full_request_url, headers=headers)

    successful_request = True
    if gizmo_request.status_code != 200:
        # raise ValueError("Error Fetching Gizmo JSON @ URL " + full_request_url +  " Status Code: " + str(gizmo_request.status_code) + " " + gizmo_request.text)
        return None, False, "http_code " + str(gizmo_request.status_code)

    gizmo_json = None
    try:
        gizmo_json = gizmo_request.json()
    except:
        print("Error Fetching Gizmo JSON @ URL " + full_request_url + " Status Code: " + str(gizmo_request.status_code))
        return (gizmo_json, False, "invalid_json")

    return (gizmo_json, successful_request, "none")

def decode_scrapers(name):
    match name:
        case "topgpts.ai":
            return TopGPTsScraper()
        case _:
            raise ValueError(f"Unknown scraper name/Not implemented: {name}")
def main():
    failure_tracker = {}
    title = 'Select scrapers to run: '
    options = ['topgpts.ai', 'plugin.surf', 'Twitter']
    selected = pick(options, title, multiselect=True, min_selection_count=1)

    selected_strings = "Running with "
    for i in selected:
        selected_strings = selected_strings +  i[0] + ", "

    print(f"{scraperutils.bcolors.OKCYAN}{selected_strings}{scraperutils.bcolors.ENDC}")

    scrapers = []
    for selection in selected:
        scrapers.append(decode_scrapers(selection[0]))

    scraper_data = []
    for scraper in scrapers:
        # TODO: check if a .bak.json of the output exists and ask if you want to ignore scraping

        openai_urls = scraper.scrape()
        scraper_data.append({
            "id": scraper.ID,
            "scraper": scraper,
            "openai_urls": openai_urls,
            "openai_gpts": []
        })

    # compose the urls into referral banks
    referrer_lookup_table = {}

    gizmo_list = []
    for scraper in scraper_data:
        for openai_url in scraper["openai_urls"]:
            # Take the gizmo and fetch OpenAI data
            gizmo, status, reason = fetch_openai_gizmo(openai_url)

            if status == False:
                if reason not in failure_tracker.keys():
                    failure_tracker[reason] = 1
                else:
                    failure_tracker[reason] += 1

                continue

            # Case for if the gizmo appears in another scrape, we will not append it, but we will keep a log of it
            if openai_url in referrer_lookup_table.keys():
                print(f"{scraperutils.bcolors.OKCYAN}Duplicate OpenAI URL: {openai_url}")
                referrer_lookup_table[openai_url].append(scraper["id"])
            else:
                referrer_lookup_table[openai_url] = [scraper["id"]]
                gizmo_list.append(gizmo)


    # At the end of it all, look for gizmos with that data and
    print(f"{scraperutils.bcolors.WARNING}Failures = ", failure_tracker)


def exit():
    pass


if __name__ == "__main__":
    main()

