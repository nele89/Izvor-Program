@echo off
title Pokretanje AI Trgovinskog Bota
color 0A
echo.
echo 🧠 Pokrećem AI Trgovinskog Bota...
echo ===============================

:: Provera da li je Python dostupan
where python >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Python nije pronadjen. Proveri da li je instaliran ili dodat u PATH.
    echo.
    pause
    exit /b
)

:: Pokretanje aplikacije
python start.py

echo.
echo ✅ Bot je zavrsio rad ili je zatvoren.
pause
