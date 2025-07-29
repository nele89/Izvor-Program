import os
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
from logs.logger import log

# Putanja do sačuvanog modela
MODEL_PATH = os.path.join("ai", "models", "sentiment_model")

# Učitavanje modela i tokenizatora van funkcije (da se ne učitava svaki put iznova)
try:
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
except Exception as e:
    tokenizer = None
    model = None
    log.error(f"❌ Greška pri učitavanju sentiment modela/tokenizatora: {e}")

# Mapa za klasifikaciju
LABEL_MAP = {0: "negativan", 1: "neutralan", 2: "pozitivan"}

def predict_sentiment(text: str) -> str:
    if not tokenizer or not model:
        log.error("❌ Model ili tokenizer nisu učitani.")
        return "nepoznato"
    
    try:
        # Priprema ulaza
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        with torch.no_grad():
            outputs = model(**inputs)

        # Predikcija
        predicted_class = torch.argmax(outputs.logits, dim=1).item()
        return LABEL_MAP.get(predicted_class, "nepoznato")

    except Exception as e:
        log.error(f"❌ Greška u predikciji sentimenta: {e}")
        return "nepoznato"
