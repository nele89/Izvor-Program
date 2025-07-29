import os
import configparser
from dotenv import load_dotenv

load_dotenv()

def load_mt5_credentials():
    config = configparser.ConfigParser()
    config.read("config/config.ini")  # ispravna putanja

    # Pročitaj direktne vrednosti iz config.ini
    direct_login = config.get("MT5", "login", fallback="")
    direct_password = config.get("MT5", "password", fallback="")
    direct_server = config.get("MT5", "server", fallback="")
    direct_path = config.get("MT5", "path", fallback="")

    # Pročitaj imena promenljivih iz .env (ako postoje)
    login_env = config.get("MT5", "login_env", fallback="MT5_LOGIN")
    password_env = config.get("MT5", "password_env", fallback="MT5_PASSWORD")
    server_env = config.get("MT5", "server_env", fallback="MT5_SERVER")
    path_env = config.get("MT5", "path_env", fallback="MT5_PATH")

    # Proveri da li postoje promenljive u .env, ako ne — koristi direktne vrednosti
    login = os.getenv(login_env, direct_login)
    password = os.getenv(password_env, direct_password)
    server = os.getenv(server_env, direct_server)
    path = os.getenv(path_env, direct_path)

    return {
        "login": login,
        "password": password,
        "server": server,
        "path": path
    }

def connect_with_env():
    from backend.mt5_connector import connect_to_mt5
    creds = load_mt5_credentials()

    if not all([creds["login"], creds["password"], creds["server"], creds["path"]]):
        print("❌ Nedostaju MT5 kredencijali!")
        return False

    return connect_to_mt5(
        path=creds["path"],
        login=int(creds["login"]),
        password=creds["password"],
        server=creds["server"]
    )
