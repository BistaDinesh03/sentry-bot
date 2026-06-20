@echo off
echo Creating Sentry Bot auto-start task...
schtasks /create /tn "SentryBot" /tr "C:\Users\dines\sentry\START.bat" /sc onstart /delay 0001:00 /f
echo.
echo Done! Bot will auto-start when Windows boots.
echo.
pause