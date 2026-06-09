# Carbon Footprint Awareness Platform 🌱

> **Challenge Vertical:** [Challenge 3] Carbon Footprint Awareness Platform  
> *Design a solution that helps individuals understand, track, and reduce their carbon footprint through simple actions and personalized insights.*

---

## 🔗 Live Demo

**<https://carbon-tracker-gulb.onrender.com>**

> Running as a multi-stage Docker container on Render with live Gemini (Vertex AI) insights and Supabase-backed tracking.

---

## 1. Chosen Vertical

**Carbon Footprint Awareness Platform** — A tool for individuals who want to track their daily emissions and learn how to reduce them. The platform calculates deterministic CO₂e footprints and provides personalized, AI-generated strategies to drive behavioral change.

---

## 2. Approach and Logic

### Decision Flow

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

### Core Logic
1. **Deterministic Math Engine** (`carbon_calc.py`): Pure functions calculate CO₂e using cited emission factors (India CEA 2023, IPCC AR6, US EPA WARM).
2. **Hybrid AI Engine** (`eco_concierge.py`): Generates contextual tips using Gemini. If the API is unreachable, it defaults to a static rules-based generator.
3. **Dependency Injection**: FastAPI `Depends()` is used to inject Database and AI clients dynamically, keeping service functions pure.
4. **Non-Blocking Architecture**: Heavy AI text generation runs via `FastAPI.BackgroundTasks` to prevent blocking the HTTP event loop.

---

## 3. How the Solution Works

### Features
1. **Calculate** — Select a category (Energy, Transit, Waste), enter daily metrics, and receive a CO₂e score.
2. **Reduce** — The AI Eco-Concierge generates a specific reduction strategy based on your input.
3. **Track** — View historical emissions via interactive Recharts.
4. **Gamify** — Compare total footprint against other anonymous users on the Leaderboard.
5. **Automate** — Use the receipt parser to extract values directly from utility bills via Gemini Vision.

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

**Render Deployment:**
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
- **AI Degradation**: The Gemini API integration is best-effort. The fallback rule engine handles offline or missing-key scenarios.

---

## 8. Evaluation Rubric Mapping

| Axis | Implementation Details |
|------|---------------|
| **Code Quality** | Typed end-to-end (`Pydantic v2` + `TypeScript Strict`). Uses dependency injection (`app/deps.py`) to decouple Database and AI clients. Implements pure mathematical functions for CO₂e logic. |
| **Security** | Implements security headers middleware (`CSP`, `HSTS`, `X-Frame-Options`) and `slowapi` rate-limiting. Secrets are managed via environment variables and excluded from the repository. Container runs as a non-root user. |
| **Efficiency** | Progressive Web App (PWA) uses a Service Worker for offline caching. Asynchronous `BackgroundTasks` offload AI generation. Deployed as a multi-stage Docker image. |
| **Testing** | `pytest` backend suite verifies mathematical calculations and endpoint routing. `vitest` tests frontend components alongside `axe-core` accessibility checks. Tested automatically via GitHub Actions CI. |
| **Accessibility** | Uses visually hidden data tables (`.sr-only`) backing Recharts graphs. Includes skip-to-content links and bound `<label>` controls. Implements `aria-live` for dynamic AI insights. |
| **Google Services** | Integrates Google Gemini for dynamic Eco-Concierge generation and utility receipt parsing. |
| **Problem Statement Alignment** | Aligns with the "Understand → Track → Reduce" framework. Calculates baselines, tracks progress via leaderboards, and provides Gemini-powered reduction strategies. |
