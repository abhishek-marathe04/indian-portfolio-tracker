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

# 2. Build the React frontend
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

For frontend-only development with hot reload, run `npm run dev` inside `frontend/` (proxies API calls to the backend on port 8000).

---

## Getting Your Data In: CAS Statements

Your portfolio starts out empty — it fills up when you upload **Consolidated Account Statement (CAS)** PDFs from CDSL/NSDL (covers mutual funds, demat equity holdings, and NPS in one file). There are two ways to get CAS files:

1. **Manual** — request/download a CAS PDF yourself from the [CDSL](https://www.cdslindia.com/) or [CAMS/KFintech](https://www.camsonline.com/) portal and upload it directly.
2. **Automated (recommended)** — use the included Google Apps Script (below) to pull every CAS PDF that's ever landed in your Gmail inbox and drop them into one Drive folder, so you can bulk-download and bulk-upload them in one shot.

### Option A: Automate CAS collection with Google Apps Script

CDSL emails you a CAS PDF (as an attachment) periodically or whenever you request one. Instead of hunting through your inbox, [`code.gs`](code.gs) in this repo is a small Google Apps Script that searches Gmail for those emails and saves every attachment into a Drive folder you choose.

**Setup (one-time, ~5 minutes):**

1. **Create a Drive folder** to hold the statements, e.g. "CAS Statements". Open it and copy the folder ID from the URL:
   `https://drive.google.com/drive/folders/`**`<this-part-is-the-folder-id>`**
2. Go to [script.google.com](https://script.google.com) → **New project**.
3. Delete the placeholder code and paste in the contents of [`code.gs`](code.gs) from this repo.
4. Replace the `folderId` value at the top of `savePastAttachments()` with the folder ID you copied in step 1.
5. (Optional) Adjust `searchQuery` if your statements arrive under a different subject line — the default matches CDSL's standard CAS email subject.
6. Click **Run** (▶) on `savePastAttachments`. The first run will prompt you to authorize the script's access to Gmail and Drive — this is expected; the script only runs in your own Google account and nothing leaves it.
7. Check the **Execution log** (`View → Logs`, or `Ctrl/Cmd+Enter`) to see which files were saved. The script skips files already saved, so it's safe to re-run any time new statements arrive.
8. Open the Drive folder — your CAS PDFs should now be there.

> The script processes up to 50 matching email threads per run (Apps Script has a ~6 minute execution limit). If you have more than that, just click Run again — already-saved files are skipped automatically.

**Optional: keep it running automatically.** In the Apps Script editor, go to **Triggers** (clock icon) → **Add Trigger** → choose `savePastAttachments`, event source "Time-driven", and pick a schedule (e.g. daily). New CAS emails will then be archived to Drive without you doing anything.

### Option B: Bulk-upload into the app

Once your CAS PDFs are sitting in that Drive folder:

1. Download the whole folder locally (Drive web UI: right-click the folder → **Download**, which gives you a `.zip` — unzip it).
2. Open the app and go to **Upload CAS** in the sidebar (`/upload-cas`).
3. Select all the CAS PDF files at once (multi-select is supported) and enter the CAS PDF password (CDSL/CAMS statements are password-protected — usually your PAN or a password you set when requesting the statement).
4. Submit. Each file is processed as a background job with live per-file progress (queued → processing → done/duplicate/error), so you can watch a batch of dozens of statements import without blocking the UI.
5. Once it finishes, your holdings, transactions, and portfolio value will appear across the Dashboard, Portfolio, and Performance pages.

Re-uploading a newer CAS for a folio you've already imported updates that holding rather than duplicating it — statements are matched by folio number + ISIN and only applied if they're not older than what's already stored.

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
uploads/                     ← Archived CAS PDFs
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
│   │   ├── profiles.py          # Family member profiles
│   │   ├── cas.py               # CAS upload (single + bulk) & import history
│   │   ├── assets.py            # Asset CRUD for all 15 asset types
│   │   ├── analytics.py         # Net worth, allocation, XIRR, performance
│   │   └── export.py            # CSV / Excel / HTML snapshot export
│   ├── services/
│   │   ├── encryption.py        # AES-256-GCM for PAN numbers
│   │   ├── cas_parser.py        # CAS PDF parser (CDSL/NSDL, CAMS + KFintech)
│   │   ├── price_fetcher.py     # Live prices: AMFI, NSE, CoinGecko
│   │   ├── xirr.py              # XIRR calculation
│   │   ├── scheduler.py         # APScheduler background jobs
│   │   ├── export_service.py    # Export logic
│   │   └── snapshot_generator.py # HTML snapshot generator
│   ├── tests/                   # Pytest suite (CAS parsing, import, XIRR)
│   └── data/
│       └── portfolio.db         # SQLite database
├── templates/
│   ├── placeholder.html         # Shown when frontend isn't built
│   └── dashboard_snapshot.html  # Jinja2 template for HTML export
├── frontend/                    # React 18 + TypeScript + Vite + Tailwind
│   └── src/
│       ├── pages/               # One page per asset class + dashboard/performance/upload
│       ├── components/          # Shared UI + per-feature components
│       ├── api/                 # Axios API client
│       └── lib/                 # Formatters, categories, utils (+ Vitest tests)
├── code.gs                      # Google Apps Script: archive CAS emails to Drive
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
| **Phase 2** | ✅ Complete | CAS PDF parser (CDSL/NSDL, CAMS + KFintech), full CRUD for all 15 asset types, live NAV/price fetch, net worth + allocation endpoints |
| **Phase 3** | ✅ Complete | React frontend (all asset pages, dashboard), bulk CAS upload with per-file progress, XIRR + performance tracking, frontend test suite |
| **Phase 4** | Planned | Family profiles UI polish, goals & maturity alerts UI, CSV/Excel export UI |
| **Phase 5** | Planned | Dark mode, mobile layout polish, HTML snapshot, QR code in settings |

---

## Testing

```bash
# Backend (pytest)
pytest

# Frontend (Vitest)
cd frontend
npm test
```

---

## Security Notes

- Passwords are hashed with **bcrypt** — never stored in plain text
- PAN numbers are encrypted with **AES-256-GCM** before being stored in the database
- JWT tokens expire after `SESSION_HOURS` (default 8 hours)
- The app binds to `0.0.0.0` by default to allow phone access on home WiFi — **do not run on public WiFi**
- No data is ever sent to the internet (except to free public price APIs — AMFI, NSE, CoinGecko)
- CAS PDF passwords are never stored; you re-enter them per upload
- The Google Apps Script (`code.gs`) runs entirely inside your own Google account — it only moves attachments from your Gmail to your Drive and never sends data anywhere else

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

**CAS upload fails with "incorrect password":**
CAS PDFs are password-protected by CDSL/CAMS — this is usually your PAN (uppercase, no spaces) unless you set a custom password when requesting the statement.

**Google Apps Script run fails with an authorization error:**
On first run, Apps Script requires you to explicitly grant it Gmail read and Drive write permissions for your own account — click through the "Advanced" → "Go to (unsafe)" prompt (this warning appears for all personal, unpublished scripts, including your own).
