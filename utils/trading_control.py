from logs.logger import log

trading_paused = {
    "news": False,
    "volatility": False
}

pause_reason = "none"

def pause_trading(reason):
    trading_paused[reason] = True
    set_pause_reason(reason)
    log.warning(f"⏸ Trgovanje pauzirano zbog: {reason}")

def resume_trading(reason):
    if trading_paused[reason]:
        trading_paused[reason] = False
        if not any(trading_paused.values()):
            set_pause_reason("none")
        log.info(f"▶️ Trgovanje nastavljeno (ukinut razlog: {reason})")

def is_trading_paused():
    return any(trading_paused.values())

def get_pause_reason() -> str:
    return pause_reason

def set_pause_reason(reason: str):
    global pause_reason
    pause_reason = reason
