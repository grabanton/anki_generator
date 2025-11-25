@echo off
setlocal

REM === Check input argument ===
set "CSV_FILE=%USERPROFILE%\OneDrive\Documents\English.csv"
if not "%~1"=="" (
  set "CSV_FILE=%~1"
)

REM === General paths ===
set "CSV_FILE=%USERPROFILE%\OneDrive\Documents\English.csv"

REM Path to the project and venv
set "PROJECT_ROOT=D:\Tools\anki_generator"
set "VENV_ACTIVATE=%PROJECT_ROOT%\.venv\Scripts\activate.bat"

REM User documents and base output folder
set "USER_DOCS=%USERPROFILE%\OneDrive\Documents"
set "BASE_DIR=%USER_DOCS%\AnkiEnglish"

REM Path to Anki profile via APPDATA
set "ANKI_BASE=%APPDATA%\Anki2\User 1"
set "ANKI_MEDIA=%ANKI_BASE%\collection.media"

REM Log file
set "LOG_FILE=%BASE_DIR%\anki_generator.log"

REM === Create base folder AnkiEnglish if it doesn't exist ===
if not exist "%BASE_DIR%" (
    mkdir "%BASE_DIR%"
)

REM === Get timestamp YYYY-MM-DD_HH-MM via PowerShell ===
for /f %%i in ('
    powershell -NoLogo -NoProfile -Command "Get-Date -Format \"yyyy-MM-dd_HH-mm\""
') do set "TS=%%i"

REM === Create output folder with timestamp ===
set "OUTPUT_DIR=%BASE_DIR%\%TS%"
mkdir "%OUTPUT_DIR%"

REM === Log start ===
echo [%TS%] Starting generation. CSV="%CSV_FILE%" OUTPUT_DIR="%OUTPUT_DIR%" >> "%LOG_FILE%"

REM === Activate virtual environment (.venv in project root) ===
call "%VENV_ACTIVATE%"

REM === Run card generation ===
python "%PROJECT_ROOT%\build_cards.py" "%CSV_FILE%" --output-dir "%OUTPUT_DIR%"

REM === Handle Python errors: don't copy media if generation failed ===
if errorlevel 1 goto :PYTHON_FAIL

REM === Media folder produced by the generator ===
set "MEDIA_SRC=%OUTPUT_DIR%\media"

REM === Copy media files to the Anki collection ===
if exist "%MEDIA_SRC%" (
    echo Copying media files to Anki collection...
    xcopy "%MEDIA_SRC%\*" "%ANKI_MEDIA%\" /Y /I /Q
    echo [%TS%] Copied media from "%MEDIA_SRC%" to "%ANKI_MEDIA%" >> "%LOG_FILE%"
) else (
    echo Media folder not found: "%MEDIA_SRC%"
    echo [%TS%] WARNING: media folder not found at "%MEDIA_SRC%" >> "%LOG_FILE%"
)

REM === Open output folder in Explorer ===
start "" "%OUTPUT_DIR%"

echo [%TS%] Done. >> "%LOG_FILE%"

goto :EOF


:PYTHON_FAIL
set "PY_ERR=%ERRORLEVEL%"
echo [%TS%] ERROR: build_cards.py exited with code %PY_ERR% >> "%LOG_FILE%"
echo Generation failed with exit code %PY_ERR%.
exit /b %PY_ERR%

endlocal

