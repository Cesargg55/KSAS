@echo off
REM KSAS - Candidate Re-Scanner

echo ============================================================
echo    KSAS - Candidate Re-Scanner
echo ============================================================
echo.
echo This will re-analyze all candidates and update their
echo metrics with accurate BLS power and TLS SDE values.
echo.
echo WARNING: This may take several minutes depending on
echo the number of candidates.
echo.

python rescan_candidates.py

echo.
echo ============================================================
pause
