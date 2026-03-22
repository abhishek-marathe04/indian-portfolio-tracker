#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run.sh — Start the Indian Portfolio Tracker (Linux / macOS)
#
# Usage:  ./run.sh
#
# Requires: Python 3.11+, dependencies installed via `pip install -r requirements.txt`
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── 1. Load .env ──────────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
  echo ""
  echo "  ❌  .env not found. Run 'python setup.py' first."
  echo ""
  exit 1
fi

# Export only non-comment, non-empty lines
set -a
# shellcheck disable=SC2046
export $(grep -v '^\s*#' .env | grep -v '^\s*$' | xargs)
set +a

PORT="${PORT:-8000}"
BIND_HOST="${BIND_HOST:-0.0.0.0}"

# ── 2. Detect local WiFi IP ───────────────────────────────────────────────────
LOCAL_IP=$(python3 - <<'PYEOF'
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    print(ip)
except Exception:
    print("127.0.0.1")
PYEOF
)

# ── 3. Banner ─────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🇮🇳  Indian Portfolio Tracker"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ✅  App starting at:"
echo "      Laptop  →  http://localhost:${PORT}"
echo "      Phone   →  http://${LOCAL_IP}:${PORT}  (same WiFi only)"
echo ""
echo "  ⚠️   WARNING: Do NOT run on public or shared WiFi!"
echo "      Set BIND_HOST=127.0.0.1 in .env to disable WiFi access."
echo ""

# ── 4. Print QR code for phone URL ───────────────────────────────────────────
python3 - <<PYEOF
import sys
try:
    import qrcode
    qr = qrcode.QRCode(border=1)
    qr.add_data("http://${LOCAL_IP}:${PORT}")
    qr.make(fit=True)
    print("  Scan with your phone camera to open:")
    qr.print_ascii(invert=True)
except ImportError:
    print("  (Install qrcode[pil] to see a QR code here)")
PYEOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 5. Open browser after a short delay ──────────────────────────────────────
(
  sleep 2
  if command -v open &>/dev/null; then
    open "http://localhost:${PORT}" 2>/dev/null || true   # macOS
  elif command -v xdg-open &>/dev/null; then
    xdg-open "http://localhost:${PORT}" 2>/dev/null || true   # Linux
  fi
) &

# ── 6. Start Uvicorn ──────────────────────────────────────────────────────────
cd backend
exec python3 -m uvicorn main:app \
  --host "${BIND_HOST}" \
  --port "${PORT}" \
  --reload \
  --reload-dir . \
  --log-level info
