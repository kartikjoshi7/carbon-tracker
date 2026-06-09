# Carbon Footprint Awareness Platform 🌱

> **Virtual PromptWars — Challenge 3.** A web app that helps individuals
> **understand, track, and reduce** their personal carbon footprint through
> simple inputs and **personalized, AI-generated insights**.

Built as a single, deployable web application: a **Python / FastAPI** backend and
a **React + TypeScript** frontend, using **Google Gemini** for personalized
advice and **Supabase (PostgreSQL)** for tracking, deployed to **Render** as one
Docker container.

## 🔗 Live Demo

**<https://carbon-tracker-gulb.onrender.com>**

> Running on Render with live Gemini insights and Supabase-backed
> tracking in a multi-stage Docker container.

---

## 1. Chosen Vertical

**Carbon Footprint Awareness Platform** — a tool for everyday individuals who
want to know where their emissions come from and what to actually *do* about
them. The product is organised around the three verbs in the brief:

| Pillar | In the product |
| --- | --- |
| **Understand** | Enter daily lifestyle facts → get a per-category CO₂e breakdown compared to the global average (~13.7 kg/day). |
| **Track** | Save snapshots over time (anonymously) and view historical trends via interactive charts. |
| **Reduce** | Receive personalized, *quantified* reduction tips that target your largest emission source first. |

---

## 2. Approach and Logic

### The Decision Flow

```text
User inputs (energy, transit, waste)
        │
        ▼
Carbon engine  ──►  per-category kg CO₂e  ──►  ranked by size
        │                                          │
        ▼                                          ▼
Comparison to global avg               Insights generator
(~13.7 kg CO₂e/day)                     ├─ Gemini: tailored advice for largest category
                                         └─ Rule-based fallback: deterministic,
                                            targets the biggest contributors
        │
        ▼
Save snapshot (Supabase, keyed by anonymous device id) → history & trend
```

The "logical decision making based on user context" the brief asks for shows up
in two places:

1. **The insights engine targets the user's own largest emission category** and
   gives advice specific to that contributor — a heavy AC user is told about
   energy; a solo commuter is told about carpooling; each recommendation is
   derived from that user's numbers.
2. **Graceful AI degradation.** Gemini produces the richest advice, but if it is
   unavailable (no credentials, quota, network) the platform *transparently falls
   back* to a deterministic rule engine, so the user always gets useful guidance.
   The fallback is silent — no user-facing errors.

### Emission Model

Footprint figures use published emission factors documented inline in
[`backend/app/services/carbon_calc.py`](backend/app/services/carbon_calc.py) —
every constant cites its source rather than being a magic number. All quantities
are normalised to **kg CO₂e**.

| Constant | Value | Source |
| --- | --- | --- |
| `GRID_EMISSION_FACTOR_KG_PER_KWH` | 0.82 | India CEA CO₂ Baseline Database v18, 2023 |
| `AC_POWER_DRAW_KW` | 1.5 | Bureau of Energy Efficiency (BEE) India |
| `TRANSIT_FACTORS["rickshaw"]` | 0.05 kg/km | IPCC AR6 WGIII Chapter 10, Table 10.5 |
| `TRANSIT_FACTORS["shuttle"]` | 0.02 kg/km | IPCC AR6 (high-occupancy diesel bus) |
| `TRANSIT_FACTORS["two_wheeler"]` | 0.10 kg/km | IPCC AR6 (solo petrol two-wheeler) |
| `FOOD_WASTE_FACTOR_KG_PER_GRAM` | 0.002 | US EPA WARM Model v16, 2023 |

---

## 3. How the Solution Works

### Architecture

```text
Browser (React + TS, Vite)              Render (single Docker container)
  • PWA with offline caching  ──HTTP──► FastAPI
  • anonymous device id (localStorage)    ├─ POST /api/v1/footprint/{category}
                                          ├─ POST /api/v1/footprint/upload-receipt
                                          ├─ GET  /api/v1/footprint/history/{id}
                                          ├─ GET  /api/v1/footprint/leaderboard
                                          ├─ GET  /api/health
                                          └─ GET  / (+ assets)  serves built SPA
                                              │
                                              ├─► Google Gemini API
                                              └─► Supabase (PostgreSQL)
```

One container serves both the API and the static SPA, so there is a single
service to deploy and a single origin (no CORS in production). Secrets are
injected via environment variables at deploy time — **there are no API keys or
secrets in the repository**.

### Project Layout

```text
backend/
  app/
    deps.py             Dependency injection (Supabase + Gemini clients)
    main.py             FastAPI app, security middleware, SPA serving
    routers/            API route definitions
    schemas/            Pydantic v2 request models with field constraints
    services/
      carbon_calc.py    Pure deterministic CO₂e math (cited constants)
      database.py       Supabase persistence layer
      eco_concierge.py  Gemini insights + rule-based fallback
  tests/                pytest suite (unit + integration)
frontend/               React + TypeScript SPA (Vite, Recharts, PWA)
.github/workflows/      CI: lint + type-check + test + build on every push
Dockerfile              Multi-stage build (node build → python runtime)
```

### Key Endpoints

| Method & Path | Purpose |
| --- | --- |
| `POST /api/v1/footprint/energy` | Calculate and persist energy CO₂e |
| `POST /api/v1/footprint/transit` | Calculate and persist transit CO₂e |
| `POST /api/v1/footprint/waste` | Calculate and persist waste CO₂e |
| `POST /api/v1/footprint/upload-receipt` | Gemini Vision receipt extraction |
| `GET /api/v1/footprint/history/{id}` | Fetch a device's history (newest first) |
| `GET /api/v1/footprint/leaderboard` | Top users ranked by lowest total CO₂e |
| `GET /api/health` | Liveness / readiness probe |

---

## 4. Running Locally

**Backend** (Python 3.12+):

```bash
cd backend
python -m venv venv && .\venv\Scripts\activate   # Windows
pip install -r requirements.txt
# No Gemini key needed locally — the rule engine activates automatically:
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend** (Node 20+):

```bash
cd frontend
npm install
npm run dev      # proxies /api to http://localhost:8000
```

**Or the whole thing as one container:**

```bash
docker build -t carbon-platform .
docker run -p 8080:8080 carbon-platform
# open http://localhost:8080
```

If `GEMINI_API_KEY` is not set, the app runs fully offline using the deterministic
rule engine and Supabase mock data.

---

## 5. Deployment

The application is deployed to **Render** as a single Docker web service.

```text
Render (Web Service)
 └── Docker Container (multi-stage, non-root)
      ├── /static/       React SPA (built by Node in stage 1)
      └── Uvicorn        FastAPI (Python runtime, stage 2, port 8080)
           ├─► Gemini API (env: GEMINI_API_KEY)
           └─► Supabase   (env: SUPABASE_URL, SUPABASE_KEY)
```

**Steps:**
1. Connect this repository to a Render Web Service (Docker environment).
2. Set these environment variables in the Render dashboard:
   ```
   SUPABASE_URL=<your Supabase project URL>
   SUPABASE_KEY=<your Supabase service-role key>
   GEMINI_API_KEY=<your Gemini API key>
   ```
3. Render builds the multi-stage Dockerfile, runs as `appuser` (non-root), and
   serves on port `8080`.

> **Live deployment:** <https://carbon-tracker-gulb.onrender.com>

---

## 6. Testing

| Suite | Command | Covers |
| --- | --- | --- |
| Backend unit | `cd backend && pytest tests/test_carbon_calc.py -v` | All 3 CO₂e functions: edge cases, boundary values, precision |
| Backend integration | `cd backend && pytest tests/test_api.py -v` | All endpoints, Pydantic 422 validation, DI mock overrides |
| Frontend components | `cd frontend && npx vitest run` | Component rendering, tab navigation, form bindings |
| Frontend a11y | `cd frontend && npx vitest run` | Automated **axe-core** assertions — zero violations |
| Lint | `ruff check app/ tests/` | Code quality gates |
| Type check | `mypy app/` (backend) · `npx tsc -b --noEmit` (frontend) | Static analysis |
| CI | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Runs all of the above on every push to `main` |

---

## 7. Assumptions Made

- **Awareness, not audit.** Emission factors are representative public averages
  for education, not certified carbon accounting; grids and lifestyles vary, so
  figures are estimates.
- **Anonymous by design.** No login. A random device id (in `localStorage`) keys
  a user's history. This minimises personal data and friction; clearing browser
  storage starts a fresh history.
- **Leaderboard is lightweight engagement.** The leaderboard ranks anonymous
  device ids and is intended as a motivational tool rather than a verified
  competitive ranking. Clearing `localStorage` resets identity — this is an
  accepted trade-off for zero-friction anonymity.
- **Gemini is best-effort.** When it is unreachable or disabled, the rule-based
  engine guarantees the app still delivers quantified advice. The fallback is
  silent and requires no user action.
- **Receipt parsing is assistive.** The Gemini Vision receipt parser reduces
  manual input friction for users with utility bills or travel receipts. If
  parsing fails, the user can still enter values manually.

---

## 8. How This Maps to the Evaluation Rubric

| Axis | Where to look |
| --- | --- |
| **Code Quality** | Typed end-to-end (Pydantic v2 + TypeScript strict). Dependency injection via [`app/deps.py`](backend/app/deps.py) decouples DB and AI clients. Pure functions in [`carbon_calc.py`](backend/app/services/carbon_calc.py) with cited emission constants. `ruff` linter + `mypy` type checks in CI. |
| **Security** | Security headers middleware in [`main.py`](backend/app/main.py) (`X-Content-Type-Options`, `X-Frame-Options`, `HSTS`, `Referrer-Policy`, `Permissions-Policy`). `slowapi` rate-limiting (10/min). Bounded Pydantic input validation. Restrictive CORS allow-list. Non-root container user. Secrets via env vars only (none in repo). |
| **Efficiency** | PWA with Service Worker offline caching. AI insight generation offloaded to `BackgroundTasks` (non-blocking). Multi-stage Docker image (node build → slim python runtime). Stateless pure calculation engine. |
| **Testing** | `pytest` backend suite covering math + routes + DI mocks. `vitest` frontend tests with automated `axe-core` a11y assertions. CI ([`ci.yml`](.github/workflows/ci.yml)) runs `ruff`, `mypy`, `pytest`, `tsc`, `vitest`, and `npm run build` on every push. |
| **Accessibility** | Visually hidden data tables (`.sr-only`) backing all charts. Skip-to-content link. Bound `<label>` controls. ARIA tablists with `aria-selected`. `aria-live="polite"` for dynamic AI insights. `aria-busy` loading states. See [`Dashboard.tsx`](frontend/src/Dashboard.tsx). |
| **Google Services** | Google Gemini via `google-generativeai` for text insights ([`eco_concierge.py`](backend/app/services/eco_concierge.py)) and multimodal Vision for receipt parsing. Cascading model fallback (tries multiple model versions before rule engine). |
| **Problem Statement Alignment** | Understand → Track → Reduce loop. Carbon engine quantifies baselines. History tracks trends. Gemini-powered insights target the largest contributor. Leaderboard sustains engagement. Receipt parser reduces input friction. |
