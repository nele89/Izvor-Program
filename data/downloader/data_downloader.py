import os
import requests
from logs.logger import log

class DataDownloader:
    def __init__(self, download_dir='data'):
        self.download_dir = download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def download_file(self, url, filename):
        filepath = os.path.join(self.download_dir, filename)
        try:
            log.info(f"Počinjem skidanje fajla sa: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            log.info(f"Uspešno skinut fajl: {filepath}")
            return filepath
        except requests.HTTPError as e:
            log.error(f"HTTP greška pri skidanju: {e}")
        except Exception as e:
            log.error(f"Greška pri skidanju fajla: {e}")
        return None

    def download_xauusd_data(self):
        # Primer URL, treba zameniti pravim linkom za podatke
        url = "https://example.com/data/xauusd.csv"
        filename = "xauusd.csv"
        return self.download_file(url, filename)


if __name__ == "__main__":
    downloader = DataDownloader()
    downloader.download_xauusd_data()
