@echo off
echo Backing up Sentry Bot...
set BACKUP_DIR=C:\Users\dines\sentry_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%
mkdir "%BACKUP_DIR%" 2>nul
xcopy "C:\Users\dines\sentry\data" "%BACKUP_DIR%\data\" /E /I /Y
xcopy "C:\Users\dines\sentry\logs" "%BACKUP_DIR%\logs\" /E /I /Y
xcopy "C:\Users\dines\sentry\config" "%BACKUP_DIR%\config\" /E /I /Y
echo Backup complete: %BACKUP_DIR%
pause