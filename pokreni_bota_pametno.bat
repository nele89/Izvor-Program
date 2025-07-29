@echo off
title Pokretanje AI Trgovinskog Bota sa Proverama

echo ✅ Proveravam config.ini...
if not exist config.ini (
    echo ⛔ config.ini nije pronadjen!
    pause
    exit /b
)

echo ✅ Proveravam .env fajl...
if not exist .env (
    echo ⛔ .env fajl nije pronadjen!
    pause
    exit /b
)

echo ✅ Proveravam bazu podataka...
if not exist db\trading_ai_core.db (
    echo 🔄 Baza nije pronadjena – pokrecem inicijalizaciju baze...
    python init_db.py
)

echo 🚀 Pokrecem bota...
python start.py
pause
