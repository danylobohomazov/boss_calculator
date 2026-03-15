from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from unicodedata import category

from main_app.jewel_found import jewel_calculator

CATEGORIES = {
    "Currency": "currency",
    "Unique Weapons": "unique-weapons",
    "Unique Armours": "unique-armours",
    "Unique Jewels": "unique-jewels",
    "Unique Accessories": "unique-accessories",
    "Skill Gems": "skill-gems",
    "Allflame Embers": "allflame-embers",
    "Unique Maps": "unique-maps",
    "Unique Flasks": "unique-flasks",
    "Fragments": "fragments",
    "Invitations": "invitations",
}

LEAGUE = "mirage"
START_URL = "https://poe.ninja/poe1/economy/"


def start_driver():
    opt = Options()
    opt.add_argument("--headless")
    opt.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=opt)
    return driver


def end_driver(driver):
    driver.quit()


def find_item_price(driver, name: str, category: str, divine_price: int = 1) -> float:
    level = "1"
    if "|" in name:
        name, level = name.split("|")
    if category == "Unique Jewels" or level == "item":
        price = jewel_calculator(name, divine_price, level)
        return price
    type_ = CATEGORIES[category]
    url = f"{START_URL}{LEAGUE}/{type_}"

    driver.get(url)

    if type_ in ["currency", "fragments", "allflame-embers"]:
        container_selector = "#main > astro-island > div > section > div > main > section > div > div > div:nth-child(2) > div"
        value_selector = "td.text-right"
    else:
        container_selector = "#main > astro-island > div > section > div > main > section > div > div > div.item-overview > div:nth-child(1) > div"
        value_selector = "td.sorted"

    container = driver.find_element(By.CSS_SELECTOR, container_selector)

    search_input = container.find_element(By.CSS_SELECTOR, "input._text-input_x7fc5_14")
    search_input.clear()
    search_input.send_keys(name)
    search_input.send_keys(Keys.RETURN)

    if category == "Skill Gems":
        # находим все label с select
        labels = container.find_elements(By.CSS_SELECTOR, "label:has(select)")

        # значения которые нужно выбрать
        values = ["1", "0-19", "No"]

        for label, value in zip(labels, values):
            select = Select(label.find_element(By.TAG_NAME, "select"))
            select.select_by_value(value)

    if category == "Unique Weapons" or category == "Unique Armours":
        # находим все label с select
        labels = container.find_elements(By.CSS_SELECTOR, "label:has(select)")

        # значения которые нужно выбрать
        values = ["1-4"]

        for label, value in zip(labels, values):
            select = Select(label.find_element(By.TAG_NAME, "select"))
            select.select_by_value(value)
    row = driver.find_element(By.CSS_SELECTOR, "table.data-table tbody tr")

    value_cell = row.find_element(By.CSS_SELECTOR, value_selector)

    price = float(value_cell.text)

    alt = None
    try:
        alt = value_cell.find_element(By.TAG_NAME, "img").get_attribute("alt")
    except:
        pass

    #img = row.find_element(By.CSS_SELECTOR, "td img").get_attribute("src")

    if alt == "Divine Orb":
        price *= divine_price

    return price


if __name__ == "__main__":
    driver = start_driver()
    items = [
        {
            "name": "Syndicate Medallion",
            "category": "Fragments",
        },
        {
            "name": "Voidforge",
            "category": "Unique Weapons",
        },
        {
            "name": "Svalinn",
            "category": "Unique Armours",
        },
        {
            "name": "Voices",
            "category": "Unique Jewels",
        },
        {
            "name": "Awakened Enlighten Support",
            "category": "Skill Gems",
        },
        {
            "name": "Allflame Ember of Kulemak",
            "category": "Allflame Embers",
        },
        {
            "name": "Cortex",
            "category": "Unique Maps",
        },
        {
            "name": "Progenesis",
            "category": "Unique Flasks",
        },
        {
            "name": "Mirror of Kalandra",
            "category": "Currency",
        },
        {
            "name": "Dissolution of the Flesh",
            "category": "Unique Jewels",
        },
        {
            "name": "Watcher's Eye|85",
            "category": "Unique Jewels",
        },
        {
            "name": "Watcher's Eye|87",
            "category": "Unique Jewels",
        },
        {
            "name": "Thread of Hope|86M",
            "category": "Unique Jewels",
        },
        {
            "name": "Thread of Hope|87",
            "category": "Unique Jewels",
        },
        {
            "name": "Bitterbind Point|item",
            "category": "Unique Armours",
        },
        {
            "name": "Cinderswallow Urn|item",
            "category": "Unique Flasks",
        },
    ]
    for _ in range(10):
        print(find_item_price(driver, "Thread of Hope|86M", "Unique Jewels", 225))
    #for item in items:
    #    print(item["name"])
    #    print(find_item_price(driver, item["name"], item["category"], 225))
    end_driver(driver)
