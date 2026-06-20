@echo off
title Sentry Bot Watchdog
echo ================================
echo SENTRY WATCHDOG - Auto Restart
echo ================================
echo.
echo Bot will auto-restart if crashed
echo Press Ctrl+C TWICE to stop
echo.

:loop
echo [%date% %time%] Starting Sentry Bot...
python src/main.py
echo.
echo [%date% %time%] Bot stopped. Restarting in 10 seconds...
timeout /t 10 /nobreak
goto loop