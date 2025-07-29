# ml/experience_memory.py

from datetime import datetime
from collections import deque

class DecisionMemory:
    def __init__(self, settings):
        self.settings = settings
        self.memory = deque(maxlen=int(settings.get("ai_training_last_n", 500)))

    def record(self, symbol, df, score, action):
        """Pamti AI odluku za kasniju analizu i trening."""
        if df is None or df.empty:
            return

        last_time = df.index[-1]  # poslednji trenutak u DataFrame-u
        entry = {
            "symbol": symbol,
            "timestamp": last_time,
            "score": score,
            "action": action
        }
        self.memory.append(entry)

    def get_recent(self, n=None):
        """Vrati poslednjih N odluka (ili sve ako N nije zadato)."""
        if n:
            return list(self.memory)[-n:]
        return list(self.memory)

    def clear(self):
        """Prazni memoriju (npr. posle treninga)."""
        self.memory.clear()
