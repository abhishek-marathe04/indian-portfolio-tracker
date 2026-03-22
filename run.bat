@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM run.bat — Start the Indian Portfolio Tracker (Windows)
REM
REM Usage:  run.bat   (from the project root folder)
REM
REM Requires: Python 3.11+, dependencies installed via `pip install -r requirements.txt`
REM ─────────────────────────────────────────────────────────────────────────────
setlocal EnableDelayedExpansion

cd /d "%~dp0"

REM ── 1. Check .env ─────────────────────────────────────────────────────────
if not exist ".env" (
    echo.
    echo   [ERROR] .env not found. Run "python setup.py" first.
    echo.
    pause
    exit /b 1
)

REM ── 2. Load .env into environment ─────────────────────────────────────────
for /f "usebackq tokens=1,* delims==" %%A in (`findstr /v "^#" .env`) do (
    if not "%%A"=="" (
        set "%%A=%%B"
    )
)

if "%PORT%"=="" set PORT=8000
if "%BIND_HOST%"=="" set BIND_HOST=0.0.0.0

REM ── 3. Detect local WiFi IP ───────────────────────────────────────────────
for /f %%I in ('python -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect((\"8.8.8.8\",80)); print(s.getsockname()[0]); s.close()" 2^>nul') do set LOCAL_IP=%%I
if "%LOCAL_IP%"=="" set LOCAL_IP=127.0.0.1

REM ── 4. Banner ─────────────────────────────────────────────────────────────
echo.
echo ====================================================
echo   Indian Portfolio Tracker
echo ====================================================
echo.
echo   App starting at:
echo     Laptop  -^>  http://localhost:%PORT%
echo     Phone   -^>  http://%LOCAL_IP%:%PORT%   (same WiFi only)
echo.
echo   WARNING: Do NOT run on public or shared WiFi!
echo   Set BIND_HOST=127.0.0.1 in .env to disable WiFi access.
echo.

REM ── 5. Print QR code ──────────────────────────────────────────────────────
python -c "import qrcode; qr=qrcode.QRCode(border=1); qr.add_data('http://%LOCAL_IP%:%PORT%'); qr.make(fit=True); print('  Scan with your phone camera:'); qr.print_ascii(invert=True)" 2>nul || echo   (Install qrcode[pil] to see a QR code here)

echo.
echo ====================================================
echo.

REM ── 6. Open browser ───────────────────────────────────────────────────────
start "" "http://localhost:%PORT%"

REM ── 7. Start Uvicorn ──────────────────────────────────────────────────────
cd backend
python -m uvicorn main:app --host %BIND_HOST% --port %PORT% --reload --log-level info
