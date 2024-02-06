# metascraper.py - Call the other scrapers to grab OpenAI URLs
# This script puts it all together- takes the universal interface of OpenAI URLS, calls OpenAI
# And generates JSONS of them
import argparse
import time
import traceback

import requests
import config
from pick import pick
import scraperutils
from scrapers.allgptsscraper import AllGPTSScraper
from scrapers.assistanthuntscraper import AssistantHuntScraper
from scrapers.botsbarnscraper import BotsBarnScraper
from scrapers.pluginsurfscraper import PluginSurfScraper
from scrapers.tinytopgpts import TinyTopGPTS
from scrapers.topgptsscraper import TopGPTsScraper
from scrapers.githubgptssearchscraper import GitHubGPTsSearchScraper
import json

parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('-j', '--use-json', action='store_true')
args = parser.parse_args()

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

    # wrap this in a try since sometimes urllib can error
    try:
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

    except:
        print(f"{scraperutils.bcolors.FAIL}[!] Critical URLLIB Error:\n{traceback.format_exc()}\nInvoking Mandatory Timeout of 10 minutes{scraperutils.bcolors.ENDC}")
        # Timeout for 6 minutes in case it's the server getting mad at us
        time.sleep(600)
        return (None, False, "urllib error")
def decode_scrapers(name):
    match name:
        case "topgpts.ai":
            return TopGPTsScraper()
        case "plugin.surf":
            return PluginSurfScraper()
        case "topgpts.ai-tiny":
            return TinyTopGPTS()
        case "allgpts.co":
            return AllGPTSScraper()
        case "botsbarn.com":
            return BotsBarnScraper()
        case "assistanthunt.com":
            return AssistantHuntScraper()
        case "GitHub - GPTsSearch CSV Scrape":
            return GitHubGPTsSearchScraper()
        case _:
            raise ValueError(f"Unknown scraper name/Not implemented: {name}")
def main():

    if not args.use_json:
        title = 'Select scrapers to run: '
        options = ['plugin.surf', "GitHub - GPTsSearch CSV Scrape", 'topgpts.ai', 'topgpts.ai-tiny', "allgpts.co", "botsbarn.com", "assistanthunt.com", 'Twitter']
        selected = pick(options, title, multiselect=True, min_selection_count=1)
        for i in range(len(selected)):
            selected[i] = selected[i][0]
    else:
        print(f'{scraperutils.bcolors.OKCYAN}Using preconfigured config.json{scraperutils.bcolors.ENDC}')
        with open('config.json', 'r') as f:
            config = json.load(f)
            selected = config['scrapers']
            print(f'{scraperutils.bcolors.OKCYAN}Using scrapers {selected}{scraperutils.bcolors.ENDC}')

    retry_dict = {}
    failure_tracker = {}

    selected_strings = "Running with "
    for i in selected:
        selected_strings = selected_strings + i + ", "

    print(f"{scraperutils.bcolors.OKCYAN}{selected_strings}{scraperutils.bcolors.ENDC}")

    scrapers = []
    for selection in selected:
        scrapers.append(decode_scrapers(selection))

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
        # log entry into the failure tracker
        failure_tracker[scraper.ID] = {}

    # compose the urls into referral banks
    referrer_lookup_table = {}

    #Status indicator code
    total_urls = 0
    for scraper in scraper_data:
        total_urls += len(scraper["openai_urls"])


    print(f"{scraperutils.bcolors.OKGREEN}Total URLs: {total_urls}{scraperutils.bcolors.ENDC}")

    gizmo_list = []
    for scraper in scraper_data:
        source = scraper["id"]
        for openai_url in scraper["openai_urls"]:

            # Case for if the gizmo appears in another scrape, we will not append it, but we will keep a log of it
            if openai_url in referrer_lookup_table.keys():
                print(f"{scraperutils.bcolors.OKCYAN}Duplicate OpenAI URL: {openai_url}")
                referrer_lookup_table[openai_url].append(source)
            else:
                # Take the gizmo and fetch OpenAI data
                gizmo, status, reason = fetch_openai_gizmo(openai_url)

                if status == False:
                    print(f"{scraperutils.bcolors.WARNING}Error: {reason}{scraperutils.bcolors.ENDC}")
                    # For replay reasons, we will store this in a dictionary
                    retry_dict[openai_url] = reason
                    # Log the failure for system-level reasons
                    if reason not in failure_tracker[source].keys():
                        failure_tracker[source][reason] = 1
                    else:
                        failure_tracker[source][reason] += 1
                    continue





    # At the end of it all, log the failures and which domains caused them
    print(f"{scraperutils.bcolors.WARNING}Failures = ", failure_tracker)

    with open("gizmos_noref.json", "w") as outfile:
        json.dump(gizmo_list, outfile)

    with open("replay_file.json", "w") as outfile:
        json.dump(retry_dict, outfile)

    # Let's tag all the gizmos with a referrer array
    for gizmo_index in range(len(gizmo_list)):
        gizmo_id = gizmo_list[gizmo_index]["gizmo"]["id"]
        shortcode = scraperutils.convert_short_code_to_openai_url(gizmo_id)

        if shortcode in referrer_lookup_table.keys():
            gizmo_list[gizmo_index]["source"] = referrer_lookup_table[shortcode]
        else:
            gizmo_list[gizmo_index]["source"] = ["unknown"]

    with open("gizmos_ref.json", "w") as outfile:
        json.dump(gizmo_list, outfile)


def exit():
    pass


if __name__ == "__main__":
    main()

