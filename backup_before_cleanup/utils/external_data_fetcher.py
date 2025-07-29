import requests
import os
from logs.logger import log

class ExternalDataFetcher:
    def __init__(self, api_key, base_url, save_dir="data/external"):
        self.api_key = api_key
        self.base_url = base_url
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def fetch_data(self, endpoint, params=None, filename=None):
        if params is None:
            params = {}

        params['apikey'] = self.api_key

        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            data = response.json()

            if filename:
                file_path = os.path.join(self.save_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(data, f, ensure_ascii=False, indent=4)
                log.info(f"✅ Podaci sa {endpoint} sačuvani u {file_path}")
            return data

        except requests.RequestException as e:
            log.error(f"❌ Greška prilikom preuzimanja podataka sa {endpoint}: {e}")
            return None

# Primer korišćenja
if __name__ == "__main__":
    API_KEY = "tvoj_api_kljuc"
    BASE_URL = "https://api.example.com/v1"

    fetcher = ExternalDataFetcher(API_KEY, BASE_URL)
    data = fetcher.fetch_data("marketdata", params={"symbol": "XAUUSD"}, filename="xauusd_data.json")
    print(data)
