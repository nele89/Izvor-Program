import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    AdamW,
    get_scheduler
)
from torch.utils.data import DataLoader, Dataset
import torch
from logs.logger import get_model_logger

# Putanje
MODEL_DIR = os.path.join("ai", "models", "sentiment_model")
ENCODER_PATH = os.path.join(MODEL_DIR, "sentiment_label_encoder.pkl")
logger = get_model_logger("sentiment")

class SentimentDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

def train_sentiment_model(df):
    try:
        if 'text' not in df.columns or 'label' not in df.columns:
            raise ValueError("Nedostaju kolone 'text' i/ili 'label'")

        df = df.dropna(subset=['text', 'label'])

        # Label encoding
        label_encoder = LabelEncoder()
        df['label_enc'] = label_encoder.fit_transform(df['label'])
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(label_encoder, ENCODER_PATH)

        tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')
        model = DistilBertForSequenceClassification.from_pretrained(
            'distilbert-base-uncased',
            num_labels=len(df['label_enc'].unique())
        )

        X_train, X_val, y_train, y_val = train_test_split(
            df['text'].tolist(),
            df['label_enc'].tolist(),
            test_size=0.2,
            random_state=42
        )

        train_encodings = tokenizer(X_train, truncation=True, padding=True, max_length=128)
        val_encodings = tokenizer(X_val, truncation=True, padding=True, max_length=128)

        train_dataset = SentimentDataset(train_encodings, y_train)
        val_dataset = SentimentDataset(val_encodings, y_val)

        train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=8)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)

        optimizer = AdamW(model.parameters(), lr=5e-5)
        num_training_steps = len(train_loader) * 3
        scheduler = get_scheduler("linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)

        model.train()
        for epoch in range(3):
            total_loss = 0
            for batch in train_loader:
                batch = {k: v.to(device) for k, v in batch.items()}
                outputs = model(**batch)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                total_loss += loss.item()
            logger.info(f"📚 Epoch {epoch+1} završena. Gubitak: {total_loss:.4f}")

        # Validacija (opcionalna, samo gubitak)
        model.eval()
        total_val_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                batch = {k: v.to(device) for k, v in batch.items()}
                outputs = model(**batch)
                total_val_loss += outputs.loss.item()
        logger.info(f"🧪 Validacioni gubitak: {total_val_loss:.4f}")

        # Čuvanje modela i tokenizera
        model.save_pretrained(MODEL_DIR)
        tokenizer.save_pretrained(MODEL_DIR)
        logger.info("✅ Sentiment model uspešno treniran i sačuvan.")

    except Exception as e:
        logger.error(f"❌ Greška u treniranju sentiment modela: {e}")
