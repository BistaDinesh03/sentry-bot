@echo off
title SENTRY BOT - MAX PROFIT
color 0A
echo.
echo ========================================
echo   SENTRY BOT v3.0 - MAX PROFIT EDITION
echo ========================================
echo.
echo   Scoring: 0-160 (Base 110 + 50 Boost)
echo   Filters: RSI + Volume + Momentum
echo   Exit: Trailing Stop + ATR + Time
echo   Size: Kelly Criterion
echo   Dashboard: http://localhost:8080
echo   Telegram: /s for status
echo.
echo ========================================
echo.
cd C:\Users\dines\sentry

:loop
echo [%date% %time%] Starting bot...
python src/main.py
echo.
echo [%date% %time%] Restarting in 5 seconds...
timeout /t 5 /nobreak
goto loop