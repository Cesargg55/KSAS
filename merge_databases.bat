@echo off
REM KSAS - Database Merge Utility (Windows)

echo ======================================================
echo    KSAS - Database Merge Utility
echo ======================================================
echo.
echo Merge multiple analyzed_stars.json files
echo.

python merge_databases.py %*

echo.
echo ======================================================
pause
