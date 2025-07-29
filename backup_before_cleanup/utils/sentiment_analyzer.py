from textblob import TextBlob
from logs.logger import log

def _extract_text(headline):
    """Ekstraktuje naslov iz dict ili vraća sam string."""
    if isinstance(headline, dict):
        # Traži najčešća polja za naslov
        return (
            headline.get("title") or
            headline.get("headline") or
            headline.get("summary") or
            str(headline)
        )
    return str(headline)

def analyze_sentiment(headlines):
    """
    Prima listu naslova vesti (string ili dict) i vraća 'positive', 'neutral' ili 'negative' sentiment.
    """
    if not headlines:
        return "neutral"

    polarity_total = 0
    count = 0

    for headline in headlines:
        try:
            text = _extract_text(headline)
            if not text or len(text.strip()) < 3:
                continue  # Preskoči prazne i kratke
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # vrednost između -1 i 1
            polarity_total += polarity
            count += 1
        except Exception as e:
            log.warning(f"⚠️ Greška u sentiment analizi naslova: {e}")

    if count == 0:
        return "neutral"

    avg_polarity = polarity_total / count

    if avg_polarity > 0.1:
        return "positive"
    elif avg_polarity < -0.1:
        return "negative"
    else:
        return "neutral"

if __name__ == "__main__":
    test_headlines = [
        "Gold prices surge amid economic uncertainty",
        "Investors cautious ahead of Fed decision",
        "XAUUSD steady despite mixed signals",
        {"title": "US CPI rises more than expected", "summary": "Inflation jumps..."}
    ]
    sentiment = analyze_sentiment(test_headlines)
    print(f"🧠 Detektovani sentiment: {sentiment}")
