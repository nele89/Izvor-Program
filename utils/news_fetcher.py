import requests
from logs.logger import log
from utils.settings_handler import load_settings

def fetch_latest_news(max_news=10):
    """
    Povlači najnovije vesti sa Finnhub i Marketaux, filtrira po ključnim rečima,
    vraća listu dictova: {"title": ..., "summary": ...}
    """
    settings = load_settings()
    apis = settings.get("news_apis", {})
    keywords = [kw.lower() for kw in settings.get("news_keywords", []) if kw]
    news_list = []

    # --- Finnhub ---
    finnhub_url = apis.get("primary", "")
    finnhub_token = ""
    if "token=" in finnhub_url:
        finnhub_token = finnhub_url.split("token=")[-1].strip("& ")
    if finnhub_token:
        try:
            url = f"https://finnhub.io/api/v1/news?category=general&token={finnhub_token}"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                for news in data[:max_news*2]:  # uzmi više da bi prošao filter
                    title = news.get("headline", "") or ""
                    summary = news.get("summary", "") or ""
                    text = (title + " " + summary).lower()
                    if not keywords or any(kw in text for kw in keywords):
                        news_list.append({"title": title, "summary": summary})
            else:
                log.warning(f"⚠️ Finnhub error {resp.status_code}: {resp.text[:80]}")
        except Exception as e:
            log.warning(f"⚠️ Finnhub API error: {e}")

    # --- Marketaux ---
    marketaux_url = apis.get("secondary", "")
    marketaux_key = ""
    if "apikey=" in marketaux_url:
        marketaux_key = marketaux_url.split("apikey=")[-1].strip("& ")
    if marketaux_key:
        try:
            url = f"https://marketaux.com/api/v1/news/all?api_token={marketaux_key}&symbols=XAUUSD&filter_entities=true"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                articles = data.get("data", [])
                for n in articles[:max_news*2]:
                    title = n.get("title", "") or ""
                    summary = n.get("description", n.get("summary", "")) or ""
                    text = (title + " " + summary).lower()
                    if not keywords or any(kw in text for kw in keywords):
                        news_list.append({"title": title, "summary": summary})
            else:
                log.warning(f"⚠️ Marketaux error {resp.status_code}: {resp.text[:80]}")
        except Exception as e:
            log.warning(f"⚠️ Marketaux API error: {e}")

    # Spreči duplikate po naslovu
    seen = set()
    unique_news = []
    for n in news_list:
        title = (n.get("title") or "").strip()
        if title and title not in seen:
            unique_news.append(n)
            seen.add(title)

    return unique_news[:max_news]

# Alias za kompatibilnost
fetch_news = fetch_latest_news
