import time
import requests
import statistics

LEAGUE = "Mirage"

def safe_post(session, url, json_data, retries=5, delay=1.0):
    """Надёжный POST с повторными попытками и проверкой id в ответе"""
    for attempt in range(retries):
        try:
            r = session.post(url, json=json_data)
            data = r.json()
        except Exception:
            time.sleep(delay)
            continue

        if "id" in data and "result" in data:
            return data

        print(f"POE API error, retry {attempt+1}: {data}")
        time.sleep(delay)
    raise Exception("Trade API failed after retries")

def safe_fetch(session, url, retries=5, delay=0.5):
    """Надёжный fetch с повторными попытками"""
    for attempt in range(retries):
        try:
            r = session.get(url)
            data = r.json()
            if "result" in data:
                return data["result"]
        except Exception:
            pass
        time.sleep(delay)
    raise Exception("Fetch API failed after retries")

def jewel_calculator(name: str, divine_price: int=1, level: str="1"):
    min_level = 1
    max_level = None
    if level == "item":
        pass
    elif "M" in level:
        max_level = int(level[:2])
    else:
        min_level = int(level)
    # создаём сессию один раз для всех запросов
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.pathofexile.com",
    })

    search_url = f"https://www.pathofexile.com/api/trade/search/{LEAGUE}"
    query = {
        "query": {
            "status": {"option": "securable"},
            "name": name,
            "stats": [{"type": "and", "filters": [], "disabled": False}],
            "filters": {
                "misc_filters": {
                    "filters": {
                        "ilvl": {"min": min_level, "max": max_level},
                        "identified": {"option": "false"}
                    },
                    "disabled": False
                }
            }
        },
        "sort": {"price": "asc"}
    }

    # надёжный поиск
    data = safe_post(session, search_url, query, retries=5, delay=1.2)
    search_id = data["id"]
    ids = data["result"][:10]

    # fetch деталей
    fetch_url = f"https://www.pathofexile.com/api/trade/fetch/{','.join(ids)}?query={search_id}"
    items = safe_fetch(session, fetch_url, retries=5, delay=0.6)

    # собираем цены
    prices = []
    for i in items:
        price_data = i["listing"]["price"]
        price = price_data["amount"]
        if price_data["currency"] == "divine":
            price *= divine_price
        prices.append(price)

    return statistics.median(prices)