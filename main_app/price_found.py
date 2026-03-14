import requests

CATEGORIES = {
    "Currency": "Currency",
    "Unique Weapons": "UniqueWeapon",
    "Unique Armours": "UniqueArmour",
    "Unique Jewels": "UniqueJewel",
    "Unique Accessories": "UniqueAccessory",
    "Skill Gems": "SkillGem",
    "Allflame Embers": "AllflameEmber",
    "Unique Maps": "UniqueMap",
    "Unique Flasks": "UniqueFlask",
    "Fragments": "Fragment",
}

LEAGUE = "Mirage"  # твоя лига


CACHE = {}


def load_category(category):
    type_ = CATEGORIES[category]

    if type_ in ["Currency", "Fragment"]:
        url = f"https://poe.ninja/api/data/currencyoverview?league={LEAGUE}&type={type_}"
        key = "currencyTypeName"
    else:
        url = f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type={type_}"
        key = "name"

    data = requests.get(url, timeout=5).json()

    items = {}

    if type_ in ["Currency", "Fragment"]:
        # stack sizes
        stack_sizes = {
            d["name"]: d.get("stackSize", 1)
            for d in data["currencyDetails"]
        }

        for item in data["lines"]:
            name = item[key]
            stack = stack_sizes.get(name, 1)

            price = (item.get("chaosEquivalent") or 0) * stack

            items[name.lower()] = price

    else:
        for item in data["lines"]:
            items[item[key].lower()] = item.get("chaosValue")

    CACHE[category] = items


def find_item_price(name, category):
    name_lower = name.lower()

    if category not in CACHE:
        load_category(category)

    price = CACHE[category].get(name_lower)

    if price:
        return {
            "category": category,
            "name": name,
            "price": price
        }

    return None