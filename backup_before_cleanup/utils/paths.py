import os

# ✅ Apsolutna putanja do glavnog direktorijuma projekta (nivo iznad ovog fajla)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# ✅ Putanja do direktorijuma za modele
MODEL_DIR = os.path.join(BASE_DIR, "ai", "models")

# ✅ Putanja do direktorijuma za feature fajlove
FEATURES_DIR = os.path.join(BASE_DIR, "data", "features")

# ✅ Osiguranje da direktorijumi postoje
for directory in [MODEL_DIR, FEATURES_DIR]:
    os.makedirs(directory, exist_ok=True)
