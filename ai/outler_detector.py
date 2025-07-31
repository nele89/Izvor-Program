# ai/outlier_detector.py
# Napomena: fajl je preimenovan iz outler_detector.py u outlier_detector.py

import numpy as np
from utils.logger import log_change

class OutlierDetector:
    """
    Detektor anomalija za trgovačke podatke.
    Koristi jednostavan statistički metod (Z-score) za otkrivanje odstupanja.
    """

    def __init__(self, sensitivity: float = 3.0):
        """
        :param sensitivity: Prag za Z-score detekciju (default 3.0)
        """
        self.sensitivity = sensitivity

    def detect(self, data: list):
        """
        Detektuje anomalije na osnovu liste numeričkih vrednosti.
        :return: Lista indeksa gde su pronađene anomalije
        """
        if data is None or len(data) == 0:
            log_change("[OUTLIER_DETECTOR] ⚠️ Nema podataka za analizu.")
            return []

        try:
            arr = np.array(data, dtype=float)
            mean = np.mean(arr)
            std = np.std(arr)

            if std == 0:
                log_change("[OUTLIER_DETECTOR] ⚠️ Standardna devijacija je 0, nema anomalija.")
                return []

            z_scores = np.abs((arr - mean) / std)
            outliers = np.where(z_scores > self.sensitivity)[0].tolist()

            if outliers:
                log_change(f"[OUTLIER_DETECTOR] ⚠️ Detektovano {len(outliers)} anomalija na indeksima: {outliers}")
            else:
                log_change("[OUTLIER_DETECTOR] ✅ Nema detektovanih anomalija.")

            return outliers

        except Exception as e:
            log_change(f"[OUTLIER_DETECTOR] ❌ Greška pri detekciji anomalija: {e}")
            return []


# Debug test
if __name__ == "__main__":
    detector = OutlierDetector(sensitivity=2.5)
    sample_data = [1, 1.1, 1.2, 10, 1.3, 1.4, -5]
    anomalies = detector.detect(sample_data)
    print("Detektovane anomalije:", anomalies)
