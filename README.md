# 🇮🇳 Indian Portfolio Tracker

A self-hosted, offline-first web application that gives Indian retail investors a single unified view of all their investments — mutual funds, stocks, FDs, PPF, NPS, gold, real estate, crypto, and more.

**Privacy-first:** All data stays on your machine. No cloud. No telemetry.

---

## Prerequisites

| Tool | Minimum version | Install guide |
|---|---|---|
| Python | 3.11+ | https://python.org/downloads |
| pip | bundled with Python | — |
| Node.js | 18+ | https://nodejs.org (needed for frontend) |
| npm | bundled with Node.js | — |

---

## First-Time Setup

Run these commands **once** from the project root folder.

```bash
# 1. Install Python backend dependencies
pip install -r requirements.txt

# 2. (Optional but recommended) build the React frontend
cd frontend
npm install
npm run build
cd ..

# 3. Initialise the database and create your admin account
python setup.py
```

`setup.py` will:
- Copy `.env.example` → `.env` if `.env` doesn't exist yet
- Create `backend/data/portfolio.db` with all tables
- Prompt you to pick a **username** and **password** for local login

### ⚠️ Before you start — update your `.env` secrets

Open `.env` and replace the two placeholder values:

```dotenv
# Generate with:  python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=<paste a long random hex string here>
ENCRYPTION_KEY=<paste a different long random hex string here>
```

These are used to sign login tokens and encrypt your PAN numbers. Keep them safe and **never commit `.env` to git**.

---

## Daily Usage

```bash
./run.sh        # macOS / Linux
run.bat         # Windows
```

The script will:
1. Detect your machine's local WiFi IP address
2. Start the app on `0.0.0.0:8000` (accessible on your home network)
3. Print both the laptop URL and the phone URL
4. Display a **QR code** in the terminal — scan with your phone camera to open instantly
5. Open `http://localhost:8000` in your default browser automatically

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🇮🇳  Indian Portfolio Tracker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅  App starting at:
      Laptop  →  http://localhost:8000
      Phone   →  http://192.168.1.5:8000  (same WiFi only)

  ⚠️   WARNING: Do NOT run on public or shared WiFi!
```

---

## Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `BIND_HOST` | `0.0.0.0` | Set to `127.0.0.1` to restrict to laptop-only (disables phone access) |
| `PORT` | `8000` | TCP port the app listens on |
| `JWT_SECRET` | *(must set)* | Secret used to sign JWT login tokens |
| `SESSION_HOURS` | `8` | How many hours a login session stays valid |
| `ENCRYPTION_KEY` | *(must set)* | Key used for AES-256 encryption of PAN numbers |
| `APP_VERSION` | `1.0.0` | Shown in the health-check endpoint |

---

## Data Location

```
backend/data/portfolio.db    ← SQLite database — back this up!
uploads/                     ← Archived CAS PDFs (added in Phase 2)
exports/                     ← HTML snapshots + CSV/Excel exports
```

**Backup:** Just copy `backend/data/portfolio.db` to a safe location. The whole database is a single portable file.

---

## API Reference

- Interactive docs: `http://localhost:8000/api/docs`
- Health check: `GET http://localhost:8000/api/health`

```json
{
  "status": "ok",
  "version": "1.0.0",
  "db_status": "connected"
}
```

---

## Project Structure

```
indian-portfolio-tracker/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # SQLAlchemy setup, SQLite config
│   ├── models/                  # ORM models (one per asset class)
│   ├── routers/                 # API route modules
│   │   ├── auth.py              # Login / logout / health
│   │   ├── cas.py               # CAS upload (Phase 2)
│   │   ├── assets.py            # Asset CRUD (Phase 2)
│   │   ├── analytics.py         # XIRR, allocation (Phase 3)
│   │   └── export.py            # CSV / Excel / snapshot (Phase 4-5)
│   ├── services/
│   │   ├── encryption.py        # AES-256-GCM for PAN numbers
│   │   ├── cas_parser.py        # CAS PDF parser (Phase 2)
│   │   ├── price_fetcher.py     # Live prices: AMFI, NSE, CoinGecko
│   │   ├── xirr.py              # XIRR calculation
│   │   ├── scheduler.py         # APScheduler background jobs
│   │   ├── export_service.py    # Export logic (Phase 4)
│   │   └── snapshot_generator.py # HTML snapshot (Phase 5)
│   └── data/
│       └── portfolio.db         # SQLite database
├── templates/
│   ├── placeholder.html         # Shown when frontend isn't built
│   └── dashboard_snapshot.html  # Jinja2 template for HTML export (Phase 5)
├── frontend/                    # React 18 + TypeScript + Vite (Phase 2+)
├── uploads/                     # Archived CAS PDFs
├── exports/                     # Generated exports
├── requirements.txt
├── setup.py                     # First-time DB init + admin user creation
├── run.sh                       # Linux / macOS startup
├── run.bat                      # Windows startup
└── .env.example                 # Configuration template
```

---

## Phase Roadmap

| Phase | Status | Contents |
|---|---|---|
| **Phase 1** | ✅ Complete | Backend foundation, all data models, auth, health check, run scripts |
| **Phase 2** | ✅ Complete | CAS PDF parser (CAMS + KFintech), full CRUD for all 15 asset types, live NAV/price fetch, net worth + allocation endpoints |
| **Phase 3** | Planned | XIRR, allocation charts, benchmark comparison, tax insights |
| **Phase 4** | Planned | Family profiles UI, goals, maturity alerts, CSV/Excel export |
| **Phase 5** | Planned | Dark mode, mobile layout, HTML snapshot, QR code in settings |

---

## Security Notes

- Passwords are hashed with **bcrypt** — never stored in plain text
- PAN numbers are encrypted with **AES-256-GCM** before being stored in the database
- JWT tokens expire after `SESSION_HOURS` (default 8 hours)
- The app binds to `0.0.0.0` by default to allow phone access on home WiFi — **do not run on public WiFi**
- No data is ever sent to the internet (except to free public price APIs — AMFI, NSE, CoinGecko)
- CAS PDF passwords are never stored; you re-enter them per upload

---

## Troubleshooting

**`setup.py` fails with import errors:**
Make sure you've installed dependencies first: `pip install -r requirements.txt`

**`run.sh` says "command not found":**
Make it executable: `chmod +x run.sh`

**Port 8000 already in use:**
Change `PORT=8001` (or any free port) in your `.env` file.

**Phone can't reach the app:**
- Ensure laptop and phone are on the **same WiFi network**
- Check your firewall: allow inbound TCP on the configured port
- Verify `BIND_HOST=0.0.0.0` is set in `.env`

**Forgot password:**
Delete `backend/data/portfolio.db` and re-run `python setup.py` (this erases all data — back up first).
