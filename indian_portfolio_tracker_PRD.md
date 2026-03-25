# 🇮🇳 Indian Personal Portfolio Tracker — Product Requirements Document

**Version:** 1.2  
**Date:** March 2026  
**Target Audience:** Individual Indian investors & families  
**Deployment:** Local machine (offline-first, spin up on demand)

---

## 1. Product Overview

A self-hosted, offline-first web application that gives Indian retail investors a single unified view of their entire wealth across all asset classes — starting from CAMS/KFintech Consolidated Account Statements (CAS) and extending to manual asset entries (FD, PPF, NPS, Real Estate, Crypto, etc.). The app runs locally, stores all data in a local database, and can be spun up anytime to pick up exactly where the user left off.

### 1.1 Core Philosophy

- **Privacy first** — All data stays on your machine. No cloud, no telemetry.
- **Indian-context native** — Built around CAS, AMFI NAVs, NSE/BSE prices, Indian tax rules (STCG/LTCG), and Indian instruments (PPF, SSY, NPS, SGBs, etc.).
- **Family-aware** — Track multiple members under one roof, with per-member and consolidated views.
- **Spin-up friendly** — One command to start; app restores all previously saved data from local SQLite DB automatically.
- **Mobile-viewable** — When the laptop is on, the full app is accessible on any phone via home WiFi. When offline, a static HTML snapshot can be exported and shared to any device.

---

## 2. Goals & Non-Goals

### Goals
- Parse and ingest monthly CAS PDFs (CAMS + KFintech formats)
- Track 12+ asset classes relevant to Indian investors
- Support multiple family member profiles
- Provide net worth dashboard, allocation breakdown, XIRR, goal tracking, income tracker
- Fetch live NAV and stock prices from free public APIs
- Password-protected local login
- Export all data to CSV/Excel
- Maturity date alerts for time-bound instruments
- Same-WiFi live access from mobile browser (no app install needed)
- Static HTML dashboard export — shareable offline snapshot for mobile viewing

### Non-Goals (for v1)
- Mobile app (native iOS / Android)
- Cloud sync or remote access outside home network
- Broker API integrations (Zerodha, Groww OAuth)
- Automated tax filing
- Payment or transaction execution

---

## 3. User Personas

| Persona | Description |
|---|---|
| **Primary User** | Individual investor managing their own + family's investments, primarily on laptop |
| **Family Members** | Spouse, children (Sukanya Samriddhi), parents — tracked as sub-profiles |
| **Mobile Viewer** | Same user on phone — viewing live dashboard via WiFi or a shared HTML snapshot |

---

## 4. Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11+ with FastAPI |
| **Frontend** | React 18 + TypeScript + Vite |
| **UI Library** | shadcn/ui + Tailwind CSS |
| **Database** | SQLite (via SQLAlchemy ORM) — single `.db` file, portable |
| **PDF Parsing** | `pdfplumber` + custom CAS parser |
| **Auth** | Local password hashing (bcrypt) + JWT stored in httpOnly cookie |
| **Live Prices** | AMFI API (NAV), NSE India unofficial API / Yahoo Finance (stocks), CoinGecko (crypto) |
| **Charts** | Recharts |
| **Exports** | `openpyxl` (Excel), Python `csv` module |
| **Scheduler** | APScheduler (for daily price refresh + maturity alerts) |
| **HTML Snapshot** | Jinja2 templating — self-contained `dashboard.html` with inline Chart.js + CSS |
| **Packaging** | `run.sh` / `run.bat` script — one-command startup |

---

## 5. Architecture

```
portfolio-tracker/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # SQLAlchemy setup, SQLite config
│   ├── models/                  # ORM models (one per asset class)
│   ├── routers/                 # API route modules
│   │   ├── auth.py
│   │   ├── cas.py
│   │   ├── assets.py
│   │   ├── analytics.py
│   │   └── export.py
│   ├── services/
│   │   ├── cas_parser.py        # CAS PDF parsing logic
│   │   ├── price_fetcher.py     # Live price fetch (AMFI, NSE, CoinGecko)
│   │   ├── xirr.py             # XIRR calculation
│   │   ├── scheduler.py         # APScheduler jobs
│   │   ├── export_service.py
│   │   └── snapshot_generator.py  # Static HTML dashboard renderer
│   └── data/
│       └── portfolio.db         # SQLite database (persistent)
├── templates/
│   └── dashboard_snapshot.html  # Jinja2 template for static export
├── frontend/
│   ├── src/
│   │   ├── pages/              # Dashboard, Assets, Goals, Reports
│   │   ├── components/         # Charts, Tables, Forms, Modals
│   │   └── api/                # Axios API client
│   └── public/
├── uploads/                     # Stored CAS PDF archive
├── exports/                     # Generated HTML snapshots + CSV/Excel exports
├── requirements.txt
├── run.sh                       # Linux/Mac startup script
├── run.bat                      # Windows startup script
└── README.md
```

---

## 6. Data Models

### 6.1 Family Profile
```
Profile
  - id (PK)
  - name
  - relationship (self | spouse | child | parent | other)
  - date_of_birth
  - pan_number (optional, encrypted)
  - created_at
```

### 6.2 CAS / Mutual Funds
```
MutualFundHolding
  - id, profile_id (FK)
  - folio_number, scheme_name, scheme_code (AMFI)
  - amc_name
  - units_held, avg_nav, current_nav
  - invested_amount, current_value
  - last_updated

MutualFundTransaction
  - id, profile_id (FK), folio_number
  - transaction_date, transaction_type (purchase | redemption | switch | dividend | sip)
  - units, nav, amount
  - cas_source_file (original PDF filename)
```

### 6.3 Stocks / Equity
```
StockHolding
  - id, profile_id (FK)
  - exchange (NSE | BSE), ticker
  - company_name, isin
  - quantity, avg_buy_price, current_price
  - broker (Zerodha | Groww | Angel | other)
  - last_updated

StockTransaction
  - id, profile_id (FK)
  - ticker, transaction_date, action (buy | sell)
  - quantity, price, brokerage, notes
```

### 6.4 Fixed Deposits / Recurring Deposits
```
Deposit
  - id, profile_id (FK)
  - type (FD | RD)
  - bank_name, branch
  - principal_amount
  - interest_rate (%), compounding (monthly | quarterly | annual)
  - start_date, maturity_date
  - maturity_amount (auto-calculated)
  - is_joint (bool), joint_holder_name
  - nomination
  - notes
  - is_active
```

### 6.5 PPF / EPF / GPF
```
ProvidentFund
  - id, profile_id (FK)
  - type (PPF | EPF | GPF | VPF)
  - account_number, bank_or_employer
  - opening_balance
  - current_balance (manual update)
  - interest_rate (% — can update per year)
  - maturity_date (PPF: 15 years, extendable)
  - annual_contributions (JSON array of {year, amount})
  - employer_contribution (for EPF)
  - last_updated
```

### 6.6 Sukanya Samriddhi Yojana (SSY)
```
SukanyaSamriddhi
  - id, profile_id (FK, must be female child)
  - account_number, post_office_bank
  - date_of_birth_child, account_opening_date
  - maturity_date (21 years from opening / marriage after 18)
  - current_balance
  - interest_rate
  - annual_contributions (JSON)
  - last_updated
```

### 6.7 NPS
```
NPS
  - id, profile_id (FK)
  - pran_number
  - tier (Tier1 | Tier2)
  - fund_manager (SBI | LIC | HDFC | ICICI | Kotak | UTI | Aditya Birla)
  - scheme_preference (LC25 | LC50 | LC75 | AC | custom)
  - equity_pct, corporate_bond_pct, govt_bond_pct
  - current_nav, units_held, current_value
  - employer_contribution_annual, self_contribution_annual
  - last_updated
```

### 6.8 Gold
```
GoldHolding
  - id, profile_id (FK)
  - type (physical | SGB | digital_gold | gold_etf | gold_fund)
  - quantity_grams (for physical / digital)
  - units (for ETF / fund)
  - buy_price_per_gram_or_unit
  - current_price_per_gram_or_unit
  - purchase_date
  - sgb_series, sgb_maturity_date (for SGBs)
  - sgb_interest_rate (2.5% p.a.)
  - custodian (bank/broker/vault)
  - notes
```

### 6.9 Real Estate
```
RealEstate
  - id, profile_id (FK)
  - property_name, property_type (residential | commercial | plot | agricultural)
  - address, city, state
  - purchase_date, purchase_price
  - registration_cost, stamp_duty, other_costs
  - current_estimated_value (manual)
  - outstanding_loan_amount
  - rental_income_monthly
  - is_joint (bool), joint_holder_name
  - notes
  - last_valuation_date
```

### 6.10 US Stocks / International
```
InternationalHolding
  - id, profile_id (FK)
  - platform (Vested | INDmoney | Groww | other)
  - ticker, exchange (NYSE | NASDAQ | LSE | other)
  - company_name
  - quantity, avg_buy_price_usd
  - current_price_usd, current_price_inr
  - buy_date
  - lrs_amount_used (Liberalised Remittance Scheme tracking)
```

### 6.11 Crypto
```
CryptoHolding
  - id, profile_id (FK)
  - coin_symbol (BTC | ETH | etc.), coin_name
  - exchange (WazirX | CoinDCX | Binance | other)
  - quantity, avg_buy_price_inr
  - current_price_inr
  - last_updated
```

### 6.12 Post Office Schemes
```
PostOfficeScheme
  - id, profile_id (FK)
  - scheme_type (NSC | KVP | MIS | SCSS | POMIS | TD)
  - account_number, post_office
  - principal_amount, interest_rate
  - start_date, maturity_date
  - maturity_amount (auto-calculated)
  - payout_frequency (for MIS/SCSS: monthly | quarterly | annual | on_maturity)
  - notes
```

### 6.13 Goals
```
Goal
  - id, profile_id (FK) — optional (family-level goal)
  - name (Retirement | Child Education | Home | Wedding | Travel | Emergency Fund | custom)
  - target_amount
  - target_date
  - current_value (linked assets or manual)
  - linked_asset_ids (JSON — which holdings count toward this goal)
  - notes
```

### 6.14 Savings Account (Net Worth Context)
```
SavingsAccount
  - id, profile_id (FK)
  - bank_name, account_type (savings | current | salary)
  - account_number_last4
  - current_balance (manual update)
  - last_updated
```

---

## 7. Feature Specifications

### 7.1 Authentication
- Single-user local login with username + password
- Password hashed with bcrypt; stored in SQLite
- JWT token in httpOnly cookie (session-based)
- No registration flow needed — credentials set on first run via CLI or setup wizard
- Session expires after configurable idle time (default: 8 hours)
- Optional: lock screen after inactivity

### 7.2 CAS Upload & Parsing

**Supported CAS types:**
- CAMS CAS PDF (password-protected with PAN-based password)
- KFintech CAS PDF (password-protected)
- Combined CAS (when multiple RTAs in one PDF)
- **Consolidated / date-range CAS** — single PDF covering months or years of history (requested directly from CAMS/KFintech portal)
- **Individual monthly PDFs** — one per month, uploaded in bulk

**Bulk historical upload (drag and drop):**
- Upload page accepts multiple PDFs simultaneously via drag-and-drop or file picker
- User enters one password (assumed same PAN-based password across all files)
- Files are queued and processed sequentially in the background
- A progress panel shows per-file status in real time:
  ```
  ✅ CAS_Jan2022.pdf   — 12 transactions, 4 folios
  ✅ CAS_Feb2022.pdf   — 3 transactions, 4 folios
  ⏳ CAS_Mar2022.pdf   — processing...
  ⬜ CAS_Apr2022.pdf   — queued
  ```
- On completion: summary card shows total transactions imported, date range covered, any files that failed
- Failed files are flagged with reason (wrong password, unrecognised format, duplicate — already fully imported)

**Duplicate detection (critical for historical imports):**
- A transaction is a duplicate if: same folio number + same date + same transaction type + same units + same amount
- Duplicates are silently skipped — not counted as errors
- If an entire CAS PDF is already fully imported (all transactions are duplicates), file is marked "Already imported — skipped"
- Partial overlaps are handled gracefully — only net-new transactions from that PDF are added

**Single file upload flow (existing behaviour, unchanged):**
1. User uploads one CAS PDF + enters PDF password
2. Backend decrypts and parses using `pdfplumber`
3. Parser extracts: investor name, PAN, folio numbers, scheme names, AMFI codes, transactions, closing balances
4. Duplicates skipped; new transactions added; holdings updated
5. Original PDF archived in `uploads/` with timestamp
6. User sees summary: "X new transactions found across Y folios"

**Historical import — first-time setup guidance (shown in UI):**
> 💡 *Building your history for the first time? Request a Consolidated CAS from CAMS (mycams.com) and KFintech (kfintech.com) covering your full investment period — you'll get one PDF per RTA covering all your transactions. Upload both together here.*

**Parser must handle:**
- Multiple folios per AMC
- Dividend reinvestment transactions
- Switch in / switch out
- SIP transactions
- Stamp duty lines
- Different CAS layouts across months and years
- Consolidated CAS spanning multiple years (larger files, same format)
- Mixed RTA data in a single combined CAS

### 7.3 Manual Asset Entry

All asset types support:
- **Add / Edit / Delete** via forms (React modal forms with validation)
- **Backdated entries** — any historical date allowed
- **Import from CSV / Excel** — downloadable template per asset type + upload
- **Auto interest calculation** — for FD, RD, NSC, KVP, PPF, SSY — computed server-side based on principal, rate, compounding, tenure
- **Maturity date alerts** — instruments within 30 / 60 / 90 days of maturity are flagged on dashboard

### 7.4 Live Price Fetching

| Asset | API Source | Frequency |
|---|---|---|
| Mutual Fund NAV | AMFI (mfapi.in) — free, no key | Daily at 10 PM |
| NSE Stocks | NSE India unofficial JSON feed — free | Daily at 4 PM |
| BSE Stocks | BSE India unofficial API — free | Daily at 4 PM |
| Gold price | GoldAPI (free tier) or MCX data | Daily |
| USD/INR | ExchangeRate-API (free tier) | Daily |
| US Stocks | Yahoo Finance via `yfinance` library — free | Daily |
| Crypto | CoinGecko API (free, no key needed) | Daily |

- All prices cached locally in SQLite `price_cache` table
- Manual price override available per asset
- Scheduler runs via APScheduler (background thread, no separate process needed)
- User can trigger manual refresh from UI

### 7.5 Net Worth Dashboard

**Top-level cards:**
- Total Net Worth (all profiles combined)
- Per-profile net worth cards
- Net Worth change vs last month / last year
- Total invested vs current value (overall gain/loss %)

**Charts:**
- Asset allocation donut chart (by asset class)
- Per-profile allocation breakdown
- Net worth trend line (historical, built from snapshots)
- Equity vs Debt vs Gold vs Other split

**Snapshot system:** App takes a daily net worth snapshot to `/data/snapshots` for trend charting.

### 7.6 Analytics & Returns

#### XIRR Calculation
- Per mutual fund folio (using transaction history from CAS)
- Per stock holding
- Overall portfolio XIRR
- Goal-specific XIRR
- Algorithm: Newton-Raphson XIRR (Python `scipy` or custom implementation)

#### Asset Allocation Breakdown
- By asset class (MF, Stocks, FD, Gold, etc.)
- By risk category (Equity, Debt, Hybrid, Alternatives)
- By geography (India, US, International)
- By profile (member-wise)

#### Benchmark Comparison
- Compare portfolio returns against:
  - Nifty 50 TRI
  - Sensex TRI
  - Nifty 500 TRI
  - Custom benchmark
- Data sourced from free NSE historical data API

#### Tax Harvesting Suggestions
- Identify equity MF / stock holdings with unrealised STCG (held < 1 year) losses that can be booked to offset gains
- Flag holdings near the 1-year LTCG threshold (within 30 days of becoming long-term)
- Display LTCG tax estimate (equity: 12.5% above ₹1.25L; debt: slab rate)
- Display STCG tax estimate (equity: 20%; debt: slab rate)
- Note: Suggestions only — no tax advice disclaimer shown

#### Dividend & Interest Income Tracker
- Monthly / annual dividend income from MFs and stocks
- Interest income from FDs, RDs, PPF, SSY, Post Office schemes
- SGB interest income (2.5% p.a.)
- Rental income from real estate
- Aggregate income calendar view (month-by-month)

### 7.7 Goal Tracking
- Create goals with target amount + target date
- Optionally link specific holdings to a goal
- Progress bar: current value vs target
- Projected value at target date (using assumed return rate)
- SIP required to meet goal (reverse calculation)
- Goal health indicator: on-track / at-risk / off-track

### 7.8 Maturity & Alert Dashboard
A dedicated section showing upcoming maturities:
- FD / RD maturing in next 90 days
- NSC / KVP / Post Office schemes
- SGB redemption dates
- PPF 15-year maturity
- SSY maturity
- NPS retirement age proximity

### 7.9 Export
- Export any asset class as CSV or Excel (.xlsx)
- Export full portfolio snapshot as Excel (multi-sheet workbook)
- Export transaction history (MF, stocks)
- Export income report (dividends + interest by financial year)
- All exports downloadable via browser

### 7.10 Mobile Access — Same-WiFi Live View

When the laptop is running the app on the home network, any phone or tablet on the same WiFi can open the full app in a mobile browser — no installation needed.

**How it works:**
- On startup, `run.sh` detects the machine's local IP and prints it:
  ```
  ✅ App running at:
     Laptop  → http://localhost:8000
     Phone   → http://192.168.1.5:8000   (same WiFi only)
  ```
- FastAPI binds to `0.0.0.0` (all interfaces) instead of `localhost` only
- The local IP is also shown as a **QR code** in the Settings page — scan with phone camera to open instantly
- Full React app loads on phone — all features available (read + write)
- Auth (login) is still required on the phone session

**Security note:** Binding to `0.0.0.0` exposes the app to all devices on the local network. This is acceptable for a home WiFi environment. The app must NOT be run this way on public/shared WiFi. A clear warning is shown in Settings and printed on startup.

**Configuration:**
```
# .env
BIND_HOST=0.0.0.0        # default; change to 127.0.0.1 to disable WiFi access
PORT=8000
```

**Mobile UX requirements:**
- React layout is fully responsive — sidebar collapses to bottom tab bar on screens < 768px
- All charts (Recharts) render correctly at mobile viewport widths
- Touch-friendly tap targets (min 44px)
- No horizontal scroll on any screen
- Forms are mobile-keyboard friendly (correct input types: `number`, `date`, `tel`)

### 7.11 Static HTML Dashboard Snapshot

A self-contained, single-file HTML export of the portfolio dashboard — no server, no internet connection, no login required to view. Designed for quick at-a-glance viewing on any device.

**Trigger:** Settings → "Export HTML Snapshot" button (or auto-generated nightly by scheduler).

**What's included in the snapshot:**

| Section | Content |
|---|---|
| **Net Worth Summary** | Total net worth, invested amount, overall gain/loss %, change vs last month |
| **Asset Allocation Charts** | Donut chart by asset class; Equity/Debt/Other split — rendered as inline SVG via Chart.js |
| **Per-Asset Breakdown Tables** | Each asset class with current value, invested, gain/loss — collapsible sections |
| **Goal Progress Cards** | Each goal with progress bar, target amount, target date, on-track indicator |
| **Income Tracker** | Monthly dividend + interest income bar chart; annual income summary table |
| **Snapshot metadata** | Generated timestamp, data-as-of date (last price refresh) |

**Technical implementation:**
- Backend renders via **Jinja2** template (`dashboard_snapshot.html`)
- All chart data embedded as inline JSON in `<script>` tags
- Charts rendered by **Chart.js CDN** (or fully inlined for offline use)
- CSS fully inlined — zero external dependencies
- Single `.html` file, typically 200–500 KB
- Filename: `portfolio_snapshot_YYYY-MM-DD.html`
- Saved to `exports/` folder; also offered as browser download

**Sharing options (shown in UI):**
- Download to laptop → AirDrop / cable transfer to phone
- Save to iCloud Drive / Google Drive → open on phone
- WhatsApp to self (for quick mobile access)
- Open directly in any browser — iOS Safari, Android Chrome, etc.

**Design principles for the snapshot:**
- Matches the main app's visual style (same color palette, fonts)
- Mobile-first layout — looks great on a 390px wide phone screen
- Dark mode respects phone's system preference (`prefers-color-scheme`)
- No interactive data entry — read-only view only
- Clearly watermarked: *"Snapshot as of [date/time] — open the app for live data"*

**Auto-scheduled export (optional, off by default):**
- APScheduler can generate a fresh snapshot nightly after price refresh
- Saved to a fixed path (`exports/latest_snapshot.html`) — overwritten each time
- User can point iCloud/Google Drive sync folder to `exports/` for automatic phone delivery

---

## 8. UI / UX Specifications

### 8.1 Navigation Structure
```
Sidebar:
  ├── Dashboard (Net Worth Overview)
  ├── Portfolio
  │   ├── Mutual Funds (from CAS)
  │   ├── Stocks & Equity
  │   ├── Fixed Deposits & RD
  │   ├── PPF / EPF / GPF
  │   ├── Sukanya Samriddhi
  │   ├── NPS
  │   ├── Gold & SGBs
  │   ├── Real Estate
  │   ├── US Stocks
  │   ├── Crypto
  │   ├── Post Office Schemes
  │   └── Savings Accounts
  ├── Analytics
  │   ├── Returns (XIRR)
  │   ├── Allocation Breakdown
  │   ├── Benchmark Comparison
  │   └── Tax Insights
  ├── Income Tracker
  ├── Goals
  ├── Maturity Alerts
  ├── Family Profiles
  ├── Upload CAS
  └── Settings
       ├── Export Data (CSV / Excel)
       ├── Export HTML Snapshot
       ├── WiFi Access (QR code + local IP display)
       ├── Price Refresh
       └── Change Password
```

### 8.2 Key UX Principles
- **Mobile-responsive** — sidebar collapses to bottom tab bar on phones; all charts scale to mobile viewports
- **Touch-friendly** — all tap targets ≥ 44px; no hover-only interactions
- Dark mode support (system preference respected in both app and HTML snapshot)
- Indian number formatting (₹ with lakhs/crores — e.g., ₹12,45,000)
- Financial year view (April–March) alongside calendar year
- Loading states for all price-fetch operations
- Toast notifications for CAS upload results, maturity alerts
- Confirmation dialogs for all deletes

---

## 9. Local Setup & Startup

### 9.1 Prerequisites
```
- Python 3.11+
- Node.js 18+
- pip
```

### 9.2 First-Time Setup
```bash
# Clone / download the project
cd portfolio-tracker

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install && npm run build && cd ..

# Initialize DB + create admin user
python setup.py

# Start app
./run.sh        # Linux / Mac
run.bat         # Windows
```

### 9.3 Daily Usage (After First Setup)
```bash
./run.sh
# Opens browser at http://localhost:8000
# All previous data is auto-loaded from portfolio.db
```

### 9.4 What `run.sh` does
1. Detects machine's local WiFi IP address
2. Starts FastAPI backend on `0.0.0.0:8000` (accessible on home network)
3. Prints both laptop URL and phone URL (with QR code in terminal)
4. Serves the built React frontend as static files from FastAPI
5. APScheduler starts in background for price refresh + optional nightly snapshot
6. Opens browser automatically at `http://localhost:8000`

### 9.5 Data Location
```
backend/data/portfolio.db    ← All your data (back this up!)
uploads/                     ← Archived CAS PDFs
exports/                     ← Generated HTML snapshots + CSV/Excel exports
```

---

## 10. Security Considerations

- Password hashed with bcrypt (never stored plain)
- JWT tokens have short expiry (configurable, default 8 hours)
- **Network binding:** App binds to `0.0.0.0` by default to allow same-WiFi phone access. A prominent warning is shown at startup and in Settings: *"Do not run on public/shared WiFi"*. User can set `BIND_HOST=127.0.0.1` in `.env` to restrict to laptop-only.
- PAN numbers stored encrypted (AES-256 via `cryptography` library)
- No external API calls beyond free price APIs (no user data sent anywhere)
- CAS PDFs stored locally; password never stored (user re-enters per upload)
- HTML snapshots contain real financial data — user is warned to treat them like sensitive documents before sharing

---

## 11. Phase-wise Roadmap

### Phase 1 — Core MVP
- [ ] Auth (login + change password)
- [ ] SQLite DB setup with all models
- [ ] CAS PDF upload + parser (CAMS + KFintech) — single file
- [ ] **Bulk CAS upload** — drag and drop multiple PDFs, per-file progress panel, duplicate detection
- [ ] **Consolidated CAS support** — date-range PDFs spanning months/years
- [ ] Mutual Fund holdings view with full transaction history
- [ ] Manual entry: FD, PPF, Savings Account
- [ ] Net worth dashboard (basic)
- [ ] Live NAV fetch (AMFI)
- [ ] Export to CSV
- [ ] Same-WiFi mobile access (bind to `0.0.0.0`, print phone URL + QR on startup)

### Phase 2 — Full Asset Coverage
- [ ] Stocks (NSE/BSE live prices)
- [ ] Gold, SGBs
- [ ] NPS
- [ ] SSY
- [ ] Post Office schemes
- [ ] US Stocks + USD/INR conversion
- [ ] Crypto (CoinGecko)
- [ ] Real Estate

### Phase 3 — Analytics & Insights
- [ ] XIRR per folio + overall
- [ ] Asset allocation breakdown charts
- [ ] Benchmark comparison
- [ ] Tax harvesting suggestions
- [ ] Dividend + interest income tracker
- [ ] Net worth trend (snapshot history)

### Phase 4 — Family & Goals
- [ ] Multiple family member profiles
- [ ] Per-profile and consolidated views
- [ ] Goal creation + tracking
- [ ] Maturity alert dashboard
- [ ] Excel export (multi-sheet)

### Phase 5 — Polish
- [ ] Dark mode (app + HTML snapshot respects `prefers-color-scheme`)
- [ ] Mobile responsive layout — bottom tab bar on phones, touch-friendly targets
- [ ] **Static HTML snapshot** — Jinja2 renderer with inline Chart.js; net worth, allocation, goals, income
- [ ] Auto-nightly snapshot generation (APScheduler, off by default)
- [ ] QR code display in Settings for easy phone access
- [ ] CSV/Excel import templates for all asset types
- [ ] Financial year filter across all views
- [ ] README + setup documentation

---

## 12. Key Dependencies (requirements.txt)

```
fastapi
uvicorn[standard]
sqlalchemy
pdfplumber
pypdf2               # PDF decryption
python-jose[cryptography]   # JWT
passlib[bcrypt]      # Password hashing
cryptography         # AES encryption for PAN
apscheduler          # Background scheduler
httpx                # Async HTTP for price APIs
yfinance             # US stock prices
openpyxl             # Excel export
scipy                # XIRR calculation
python-multipart     # File upload support
pydantic[email]
python-dotenv
jinja2               # HTML snapshot templating
qrcode[pil]          # QR code generation for phone URL display
Pillow               # Required by qrcode
netifaces            # Detect local WiFi IP address at startup
```

---

## 13. Open Questions / Future Considerations

- **CAS parser robustness:** CAS PDF formats change slightly across RTAs and over time — the parser will need ongoing maintenance and a test suite with sample PDFs.
- **EPF passbook import:** EPFO provides a downloadable passbook PDF — a dedicated parser can be added in v2.
- **Zerodha P&L import:** Zerodha allows CSV export of holdings and P&L — can be added as an import option for stocks.
- **INDmoney / Vested export import:** For US stocks, these platforms offer data exports.
- **Inflation-adjusted returns:** Show real returns adjusted for CPI inflation — useful for long-term goals.
- **SMS/notification alerts:** For maturity alerts — could use local desktop notifications via `plyer`.
- **Backup & restore:** One-click backup of `portfolio.db` + restore from backup.
- **PWA (Progressive Web App):** Add a `manifest.json` and service worker to make the app installable on phone home screen — works on top of the same-WiFi access with zero extra backend work.
- **iCloud / Google Drive auto-sync for snapshots:** If the user points their `exports/` folder to a synced cloud folder, snapshots automatically appear on all their devices without any manual step.

---

*Document prepared based on user requirements — March 2026. Version 1.2 adds bulk historical CAS upload, consolidated date-range CAS support, and per-file progress tracking. This is the blueprint; features may evolve during implementation.*
