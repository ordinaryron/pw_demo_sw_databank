from playwright.sync_api import Page
import time, math

databank_url = "https://www.starwars.com/databank"
num_entries = 2548 # To-do: make this a parameter rather than having this hardcoded here
substring_to_keep = "https://www.starwars.com/"
substrings_to_remove = ["/series", "/star-wars-galaxy-map", "/video", "/news", "/eras", "/films", "/games-apps", "/interactive", "-all", "?"]

def contains_substring(item):
    return substring_to_keep in item

def bunch_of_filters(the_list):
    for substring in substrings_to_remove:
        the_list = list(filter(lambda sentence: substring not in sentence, the_list))
    the_list.remove("https://www.starwars.com/databank")
    return the_list

def special_snowflakes(the_list):
    # These entries, for whatever reason, don't appear in the alphabetical list of databank entries and need to be manually appended. This function mitigates that.
    the_list.append("https://www.starwars.com/databank/corporate-alliance")
    the_list.append("https://www.starwars.com/databank/rebel-alliance")
    the_list.append("https://www.starwars.com/databank/stass-allie")
    return the_list

def test_databank(page: Page):
    page.goto(databank_url)
    show_more_button = page.locator("#ref-1-24 > div.bound.vertical.peeking.quick-info-modal-disabled > div.peek > div > a > span.label")
    # In order to get all the databank entries, the Show More button has to be clicked repeatedly until all the entries are shown. I wouldn't have designed it that way,
    # but that's the way it is.
    while show_more_button.is_visible():
        show_more_button.click()
        time.sleep(10)
    
    links_list = page.locator("a").evaluate_all("(elements) => elements.map(el => el.href)")
    links_list_dedup = list(dict.fromkeys(links_list))
    links_list_dedup.sort()
    links_list_filtered1 = list(filter(contains_substring, links_list_dedup))
    links_list_filtered2 = bunch_of_filters(links_list_filtered1)
    links_list_filtered3 = special_snowflakes(links_list_filtered2)
    links_list_filtered3.sort()
    for link in links_list_filtered3:
        if link == "https://www.starwars.com/":
            continue
        if "databank" in link:
            file_link = link.removeprefix("https://www.starwars.com/databank/")
        else:
            file_link = link.removeprefix("https://www.starwars.com/")
        filename = "screenshots/" + file_link + ".png"
        print(filename)
        page.goto(link, timeout=180000)
        time.sleep(5)
        page.screenshot(path=filename, full_page=True)
        time.sleep(5)