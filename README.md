# Carbon Footprint Awareness Platform 🌱

> **Challenge Vertical:** [Challenge 3] Carbon Footprint Awareness Platform  
> *Design a solution that helps individuals understand, track, and reduce their carbon footprint through simple actions and personalized insights.*

---

## 🔗 Live Demo

**<https://carbon-tracker-gulb.onrender.com>**

> Running as a multi-stage Docker container on Render with live Gemini insights and Supabase-backed tracking.

---

## 1. Chosen Vertical

**Carbon Footprint Awareness Platform** — A tool for individuals who want to track their daily emissions and learn how to reduce them. The platform calculates deterministic CO₂e footprints and provides personalized, AI-generated strategies to drive behavioral change.

---

## 2. Approach and Logic

### System Architecture

```text
       Frontend                   Backend                    Cloud
┌────────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ React + TypeScript │      │ FastAPI Python  │      │ Google Gemini API │
│ Vite PWA           │──HTTP│ REST API        │──HTTP│ (Eco-Concierge)   │
└────────────────────┘      └─────────────────┘      └───────────────────┘
                                     │
                                     │HTTP
                                     ▼
                            ┌───────────────────┐
                            │ Supabase (PGSQL)  │
                            │ (History & Ranks) │
                            └───────────────────┘
```

### Logic Flow

```text
User inputs (energy, transit, waste)
        │
        ▼
Carbon engine  ──►  per-category kg CO₂e
        │
        ▼
Insights generator
  ├─ Gemini API: Tailored reduction advice based on metrics
  └─ Rule-based fallback: Deterministic tips for the largest categories
        │
        ▼
Save snapshot (Supabase, keyed by anonymous_device_id) → history & leaderboards
```

### Feature-to-Challenge Mapping

| Challenge Goal | Platform Feature | Purpose |
|----------------|------------------|---------|
| **Understand** | Carbon Engine | Quantifies daily habits into deterministic kg CO₂e metrics. |
| **Track** | History Dashboard | Visualizes the `anonymous_device_id` history via Recharts. |
| **Reduce** | Eco-Concierge | Translates raw metrics into actionable, Gemini-powered behavioral tips. |
| **Sustain Engagement** | Leaderboard | Gamifies reduction by ranking anonymous users against their peers. |
| **Reduce Friction** | Receipt Parser | Eliminates manual data entry via Gemini Vision OCR extraction. |

---

## 3. How the Solution Works

### Project Structure

```text
backend/    FastAPI app — carbon engine, AI services, routes, tests
frontend/   React + TypeScript SPA — dashboard, charts, accessibility
.github/    CI workflows
Dockerfile  Multi-stage production build
```

### Key API Endpoints

| Method & Path | Purpose |
| --- | --- |
| `POST /api/v1/footprint/energy` | Footprint breakdown for energy metrics |
| `POST /api/v1/footprint/transit` | Footprint breakdown for transit metrics |
| `POST /api/v1/footprint/waste` | Footprint breakdown for waste metrics |
| `POST /api/v1/footprint/upload-receipt` | AI vision parsing for utility bills |
| `GET /api/v1/footprint/history/{id}` | Fetch an anonymous device's history |
| `GET /api/v1/footprint/leaderboard` | Top 10 users ranked by lowest footprint |
| `GET /api/health` | Liveness/readiness probe |

---

## 4. Running Locally

**Backend (Python 3.12):**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate        # Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend (Node 20+):**
```bash
cd frontend
npm install
npm run dev
```

---

## 5. Deployment Readiness

The project is packaged as a unified multi-stage Docker container and deployed to Render.

### Deployment Architecture

```text
Render (Web Service)
 └── Docker Container
      ├── /static (React Built SPA)
      └── FastAPI (Uvicorn Port 8080)
```

**Deployment Steps:**
1. Connect the repository to a Render Web Service.
2. Set the build environment to `Docker`.
3. Configure the following environment variables in the Render dashboard:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_service_role_key
   GEMINI_API_KEY=your_gemini_api_key
   ```
4. Render automatically builds the React SPA and Python backend into a single container and serves it on port `8080`.

---

## 6. Testing

The project includes an automated test suite across the backend and frontend:

| Suite | Command | Covers |
|-------|---------|--------|
| Backend unit tests | `pytest tests/test_carbon_calc.py` | CO₂e math logic, edge cases, and boundary values |
| Backend integration | `pytest tests/test_api.py` | API routing, Pydantic validation, and dependency injection mocks |
| Frontend smoke | `npx vitest run` | Component rendering and form presence |
| Frontend a11y | `npx vitest run` | Automated axe-core accessibility assertions |
| CI | `.github/workflows/ci.yml` | `ruff`, `mypy`, `pytest`, `tsc`, and `vitest` runs on push |

---

## 7. Assumptions Made

- **Awareness, not audit**: Emission factors are public averages intended for education.
- **Anonymous by design**: A randomly generated `anonymous_device_id` (stored in `localStorage`) keys a user's history to minimize personal data collection.
- **Lightweight Leaderboard**: The leaderboard ranks anonymous device IDs. It is intended as a lightweight engagement feature to encourage footprint reduction, rather than a strictly verified competitive ranking system (clearing `localStorage` resets identity).
- **AI Degradation**: The Gemini API integration is best-effort. The fallback rule engine handles offline or missing-key scenarios.

---

## 8. Evaluation Rubric Mapping

| Axis | Implementation Details | Evidence |
|------|------------------------|----------|
| **Code Quality** | Typed end-to-end (`Pydantic v2` + `TypeScript Strict`). Uses dependency injection to decouple Database and AI clients. | [`backend/app/deps.py`](backend/app/deps.py) |
| **Security** | Implements security headers middleware (`CSP`, `HSTS`, `X-Frame-Options`) and `slowapi` rate-limiting. Non-root Docker container. | [`backend/app/main.py`](backend/app/main.py) |
| **Efficiency** | Progressive Web App (PWA) offline caching. Asynchronous `BackgroundTasks` offload AI generation. | [`backend/app/routers/footprint.py`](backend/app/routers/footprint.py) |
| **Testing** | 37+ backend tests verify calculations and routing. Frontend tests accessibility via `axe-core`. CI GitHub Actions. | [`backend/tests/test_api.py`](backend/tests/test_api.py) |
| **Accessibility** | Visually hidden data tables (`.sr-only`) back Recharts. Includes skip-to-content links and bound `<label>` controls. | [`frontend/src/Dashboard.tsx`](frontend/src/Dashboard.tsx) |
| **Google Services** | Integrates Google Gemini for dynamic Eco-Concierge generation and utility receipt parsing. | [`backend/app/services/eco_concierge.py`](backend/app/services/eco_concierge.py) |
| **Problem Statement Alignment** | Aligns with the "Understand → Track → Reduce" framework. Calculates baselines, tracks progress, provides Gemini strategies. | [`backend/app/services/carbon_calc.py`](backend/app/services/carbon_calc.py) |
