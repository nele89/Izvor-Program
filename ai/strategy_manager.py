def apply_strategy(settings, strategy_name):
    """
    Na osnovu izbora strategije postavlja AI parametre u settings rečnik.
    """
    strategy_name = strategy_name.lower()

    if strategy_name == "standardna":
        settings["ai_training_frequency"] = 100
        settings["ai_use_decision_memory"] = True
        settings["ai_training_last_n"] = 500

    elif strategy_name == "agresivna":
        settings["ai_training_frequency"] = 25
        settings["ai_use_decision_memory"] = False
        settings["ai_training_last_n"] = 100

    elif strategy_name == "konzervativna":
        settings["ai_training_frequency"] = 200
        settings["ai_use_decision_memory"] = True
        settings["ai_training_last_n"] = 1000

    elif strategy_name == "custom":
        # Ništa ne menjamo, korisnik sam unosi sve
        pass

    else:
        raise ValueError(f"❌ Nepoznata strategija: {strategy_name}")

    return settings
