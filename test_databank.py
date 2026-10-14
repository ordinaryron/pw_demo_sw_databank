from playwright.sync_api import Page, sync_playwright
import pytest

# The Star Wars Databank at starwars.com is a single page with some 2500+ entries to various Star Wars "things." Want to learn about Luke Skywalker or Glup Shitto? They're there
# in the databank. Problem is, the databank only displays a handful of entries at one time, with a "Show More" button that displays 18 new entries each time it's clicked. 
# Therefore, you have to click "Show More" approximately 145 times to display all entries. Those entries do not exist in the DOM until the button is clicked, and clicking an 
# entry opens it in the same window or tab.
#
# I, as a Star Wars completist, want to screenshot each of the entries in order to ensure they are archived for posterity, because nerds do that sort of thing. This code uses 
# Pytest and Playwright, both because they do what I want them to do and also for demonstration purposes. We:
# 
# 1. Click the Show More button whatever times is necessary to reach the point where all entries are displayed.
# 2. Gather a list of links from the page.
# 3. Filter, sort, and manipulate the list so that the end result is a list of all the databank entry URL with no oddities like YouTube or Akamai links.
# 4. Go to each entry URL, wait for it to fully load, screenshot it, and save the screenshot in a folder.

databank_url = "https://www.starwars.com/databank"
substring_to_keep = "https://www.starwars.com/"
substrings_to_remove = ["/series", "/star-wars-galaxy-map", "/video", "/news", "/eras", "/films", "/games-apps", "/interactive", "-all", "?"]

# These are a bunch of utility functions used in the filtering:

# contains_substring filters out non-starwars.com links from the list, so we get rid of Youtube, Akamai, or Google links as an obvious first step.
def contains_substring(item):
    return substring_to_keep in item

# bunch_of_filters removes links that have starwars.com in the URL, but aren't related to the Databank.
def bunch_of_filters(the_list):
    for substring in substrings_to_remove:
        the_list = list(filter(lambda sentence: substring not in sentence, the_list))
    the_list.remove("https://www.starwars.com/databank")
    return the_list

# Finally, special_snowflakes are entries that require special handling - the "actual" links are different than what ends up populated in the list.
def special_snowflakes(the_list):
    the_list.append("https://www.starwars.com/databank/corporate-alliance")
    the_list.append("https://www.starwars.com/databank/rebel-alliance")
    the_list.append("https://www.starwars.com/databank/stass-allie")
    return the_list

def test_databank(page: Page):
    with sync_playwright() as p:
        
        # Using Playwright we launch a new browser, context, and page. headless=False displays the browser so we can watch it run.
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Open the databank page. Make sure we get a good load by checking the response.
        response = page.goto(databank_url, wait_until="load")
        if response is None:
            pytest.fail("Critical: Page failed to load")
        if not response.ok:
            pytest.fail(f"Critical: Page loaded with error status: {response.status}")

        # Identify the "Show More" button. page_by_text isn't the best way to find a locator, but get_by_role doesn't consistently work here, presumably due to the flakiness of the
        # page. 
        show_more_label = page.get_by_text("Show More")
        loading_label = page.get_by_text("Loading...")

        # If one label or the other isn't there, die immediately.
        if not (show_more_label.is_visible()) or (loading_label.is_visible()):
            pytest.fail("Critical: The 'Show More' button is not present")

        # When the "Loading..." label switches to the "Show More" label, the button is ready to click. We click it until neither label is visible, which means all entries are
        # displayed.
        while (show_more_label.is_visible()) or (loading_label.is_visible()):
            loading_label.wait_for(state="hidden")
            show_more_label.wait_for(state="visible")
            show_more_label.click()
            page.wait_for_timeout(500) # Need a timeout here because the page is flaky enough that sometimes the "Show More" button needs a moment to recover

        # Grab every link on the page, then deduplicate and sort the list.
        links_list = page.locator("a").evaluate_all("(elements) => elements.map(el => el.href)")
        links_list_dedup = list(dict.fromkeys(links_list))
        links_list_dedup.sort()

        # Run through the filtering functions. The end result, links_list_filtered3, is a sorted list of all the databank links found on the page.
        links_list_filtered1 = list(filter(contains_substring, links_list_dedup))
        links_list_filtered2 = bunch_of_filters(links_list_filtered1)
        links_list_filtered3 = special_snowflakes(links_list_filtered2)
        links_list_filtered3.sort()

        # Finally, we can screenshot the entries. For each entry in the list we open the URL, grab the final part of the URL and add ".png" to serve as the file name, screenshot the 
        # page (again using Playwright's capabilities), and save the screenshot. There's a lot of waiting built in for each entry because sometimes it takes a while for the images
        # to load.
        for link in links_list_filtered3:
            if link == "https://www.starwars.com/":
                continue
            # Sometimes the URL includes "databank," sometimes it doesn't. I don't know why but I have to account for it.
            if "databank" in link:
                file_link = link.removeprefix("https://www.starwars.com/databank/")
            else:
                file_link = link.removeprefix("https://www.starwars.com/")
            filename = "screenshots/" + file_link + ".png"
            page.goto(link, wait_until="domcontentloaded", timeout=1800000)
            page.wait_for_load_state("networkidle", timeout=1800000)
            page.screenshot(path=filename, full_page=True)