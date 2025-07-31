# ai/ai_model.py

import os
import pickle
import numpy as np
from utils.logger import log_change

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

class AIModel:
    """Klasa za učitavanje i predikciju AI modela."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
        self.model = None

    def load(self) -> bool:
        """Učitava model sa diska, vraća True ako je uspešno."""
        if not os.path.exists(self.model_path):
            log_change(f"[AI_MODEL] ❌ Model fajl ne postoji: {self.model_path}")
            return False
        try:
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            log_change(f"[AI_MODEL] ✅ Model učitan: {self.model_name}")
            return True
        except Exception as e:
            log_change(f"[AI_MODEL] ❌ Greška pri učitavanju modela {self.model_name}: {e}")
            return False

    def predict(self, features: np.ndarray):
        """Predikcija modela sa validacijom ulaza."""
        if self.model is None:
            log_change(f"[AI_MODEL] ⚠️ Model {self.model_name} nije učitan.")
            return None

        if features is None or len(features) == 0:
            log_change(f"[AI_MODEL] ⚠️ Nedostaju ulazni podaci za model {self.model_name}.")
            return None

        try:
            prediction = self.model.predict(features)
            log_change(f"[AI_MODEL] ✅ Predikcija završena: {self.model_name}")
            return prediction
        except Exception as e:
            log_change(f"[AI_MODEL] ❌ Greška pri predikciji modela {self.model_name}: {e}")
            return None


# Debug test
if __name__ == "__main__":
    model = AIModel("model_scalping")
    if model.load():
        dummy_data = np.random.rand(1, 10)
        print("Predikcija:", model.predict(dummy_data))
