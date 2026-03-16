import time

from django.db.models import Q
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from main_app.jewel_found import jewel_calculator, start_session
from main_app.models import Item, Pass

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

CACHE = {}


def start_driver():
    opt = Options()
    opt.add_argument("--headless")
    opt.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=opt)
    return driver


def end_driver(driver):
    driver.quit()


def trade_finder(session, name: str, divine_price: int = 1):
    level = "1"
    gcp_price = float(CACHE["Currency"]["Gemcutter's Prism"]["price"])
    if "|" in name:
        name, level = name.split("|")
    price = jewel_calculator(session, name, divine_price, gcp_price, level)
    return price

def cache_clear():
    global CACHE
    CACHE = {}

def better_finder(name: str = "Divine Orb", category: str = "Currency", divine_price: int = 1):
    if CACHE[category][name]["alt"] == "Divine Orb":
        return float(CACHE[category][name]["price"]) * divine_price
    return float(CACHE[category][name]["price"])


def new_logic(driver):
    # Poe ninja cache
    for category in CATEGORIES.keys():
        start = time.time()
        if category == "Unique Jewels":
            continue
        CACHE[category] = {}
        type_ = CATEGORIES[category]
        url = f"{START_URL}{LEAGUE}/{type_}"
        print(type_)
        driver.get(url)

        if type_ in ["currency", "fragments", "allflame-embers"]:
            container_selector = "#main > astro-island > div > section > div > main > section > div > div > div:nth-child(2) > div"
            value_selector = "td.text-right"
        else:
            container_selector = "#main > astro-island > div > section > div > main > section > div > div > div.item-overview > div:nth-child(1) > div"
            value_selector = "td.sorted"

        container = driver.find_element(By.CSS_SELECTOR, container_selector)

        if category == "Skill Gems":
            # находим все label с select
            labels = container.find_elements(By.CSS_SELECTOR, "label:has(select)")

            # значения которые нужно выбрать
            values = ["1", "0-19", "No"]

            for label, value in zip(labels, values):
                select = Select(label.find_element(By.TAG_NAME, "select"))
                select.select_by_value(value)

        if type_ == "unique-weapons" or type_ == "unique-armours":
            # находим все label с select
            labels = container.find_elements(By.CSS_SELECTOR, "label:has(select)")

            # значения которые нужно выбрать
            values = ["1-4"]

            for label, value in zip(labels, values):
                select = Select(label.find_element(By.TAG_NAME, "select"))
                select.select_by_value(value)

        while True:
            try:
                show_more = driver.find_element(By.CSS_SELECTOR, "button.button.bg-coolgrey-800")
                show_more.click()
                # иногда нужно чуть подождать, чтобы данные загрузились
                time.sleep(0.1)
            except:
                # кнопка больше не найдена → все данные загружены
                break

        items = [item.name for item in Item.objects.filter(type=category)] + [item.name for item in Pass.objects.filter(type=category)]
        if category == "Currency":
            items += ["Divine Orb", "Gemcutter's Prism"]
        items = set(items)
        # теперь можно брать все строки таблицы
        rows = driver.find_elements(By.CSS_SELECTOR, "table.data-table tbody tr")
        for row in rows:
            name_cell = row.find_element(By.CSS_SELECTOR, "td:first-child")
            name = name_cell.text.split("\n")[0]
            if ","in name:
                name = name.split(",")[0]
            if name in items:
                item_dict = {}
                value_cell = row.find_element(By.CSS_SELECTOR, value_selector)
                alt = None
                try:
                    alt = value_cell.find_element(By.TAG_NAME, "img").get_attribute("alt")
                except:
                    pass
                price = float(value_cell.text)
                item_dict["price"] = price
                item_dict["alt"] = alt
                CACHE[category][name] = item_dict
        print(f"Items count: {len(items)}; Cache count: {len(CACHE[category])}")
        print(f"Time taken: {time.time() - start}\n")
    # Poe trade cache
    items = list({item.name: item for item in Item.objects.filter(Q(name__contains="|") | Q(type="Unique Jewels"))}.values())
    start = time.time()
    divine_price = int(better_finder())
    CACHE["Unique Jewels"] = {}
    session = start_session()
    for item in items:
        start_timer = time.time()
        print(item.name)
        CACHE[item.type][item.name] = {"price": trade_finder(session, item.name, divine_price), "alt": "Chaos Orb"}
        print(f"Time taken: {time.time() - start_timer}\n")
    print(f"Time taken: {time.time() - start}\n")


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
    new_logic(driver)
    # for item in items:
    #    print(item["name"])
    #    print(find_item_price(driver, item["name"], item["category"], 225))
    end_driver(driver)
