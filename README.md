# Smart Campus Sustainability Engine 🌱

> **Challenge Vertical:** [Challenge 3] Carbon Footprint Awareness Platform  
> *Design a solution that helps individuals understand, track, and reduce their carbon footprint through simple actions and personalized insights.*

---

## 🔗 Live Demo

**<https://carbon-tracker-gulb.onrender.com>**

> Running as a multi-stage Docker container on Render with live Gemini (Vertex AI) insights and Supabase-backed tracking.

---

## 1. Chosen Vertical

**Carbon Footprint Awareness Platform** — This project tackles Challenge 3 by providing a complete carbon tracking and reduction system tailored to university students. It combines deterministic CO₂e mathematical calculations with AI-generated personalized reduction strategies to create an actionable assistant.

---

## 2. Approach and Logic

### Architecture
The application follows a decoupled monorepo architecture with a FastAPI backend and a React (Vite) frontend:

```text
┌─────────────────┐     HTTP/JSON      ┌──────────────────────┐
│   React + Vite   │ ◄─────────────────► │   FastAPI Backend     │
│   (TypeScript)   │                     │   (Python 3.12)       │
│                  │                     │                       │
│  ┌────────────┐  │                     │  ┌────────────────┐   │
│  │ Dashboard  │  │                     │  │ Pydantic v2    │   │
│  │ Analytics  │  │                     │  │ Schemas        │   │
│  │ Leaderboard│  │                     │  ├────────────────┤   │
│  └────────────┘  │                     │  │ Carbon Calc    │   │
│                  │                     │  │ (Deterministic)│   │
│  Recharts        │                     │  ├────────────────┤   │
│  PWA             │                     │  │ Eco-Concierge  │   │
│                  │                     │  │ (Gemini + FB)  │   │
└─────────────────┘                     │  ├────────────────┤   │
                                        │  │ Supabase DB    │   │
                                        │  └────────────────┘   │
                                        └──────────────────────┘
```

### Core Decision-Making Logic
1. **Deterministic Math Engine** (`carbon_calc.py`): Pure functions calculate CO₂e using cited emission factors (India CEA 2023, IPCC AR6, US EPA WARM):
   - Energy: `((ac_hours × AC_POWER_KW × GRID_EF) / roommates) + ((shared_kwh × GRID_EF) / roommates)`
   - Transit: `(distance × mode_factor) / passengers`
   - Waste: `grams × FOOD_WASTE_FACTOR`

2. **Hybrid AI Engine** (`eco_concierge.py`): Attempts Gemini API for contextual tips. If the API key is missing or the network fails, it falls back to a static rules-based generator matching the university student persona.

3. **Enterprise Dependency Injection**: The backend utilizes FastAPI's `Depends()` to inject Database and AI clients dynamically, ensuring thread-safety and eliminating global state overhead.

4. **Non-Blocking Architecture**: Heavy AI text generation is offloaded to `FastAPI.BackgroundTasks`, ensuring the UI never blocks while waiting for the LLM.

---

## 3. How the Solution Works

### For the User
1. **Track** — Select a category (Energy, Transit, Waste), fill in daily metrics, and instantly receive a CO₂e score.
2. **Learn** — The AI Eco-Concierge generates a personalized reduction tip.
3. **Analyze** — View historical emissions via interactive Recharts.
4. **Compete** — Rank on the gamified Leaderboard.
5. **Upload** — Use the AI Receipt Parser to extract values from utility bills.

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

The project is built to run natively in the cloud via a single Docker container. 

**Build and Run with Docker:**
```bash
docker build -t carbon-engine .
docker run -p 8080:8080 -e SUPABASE_URL=YOUR_URL -e SUPABASE_KEY=YOUR_KEY carbon-engine
```

**Environment Variables Required:**
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
GEMINI_API_KEY=your_gemini_api_key   # Optional
```

---

## 6. Testing

The project includes an automated test suite across the backend and frontend:

| Suite | Command | Covers |
|-------|---------|--------|
| Backend unit tests | `pytest tests/test_carbon_calc.py` | CO₂e functions: edge cases, boundary values, precision, type checks |
| Backend integration | `pytest tests/test_api.py` | API endpoints, Pydantic validation (422s), response structure, mocked DI clients |
| Frontend smoke | `npx vitest run` | Component rendering, tab navigation, form presence |
| Frontend a11y | `npx vitest run` | Automated axe-core assertions |
| CI | `.github/workflows/ci.yml` | `ruff` check, `mypy`, `pytest`, `tsc`, `vitest`, build |

---

## 7. Assumptions Made

- **Awareness, not audit**: Emission factors are public averages for education. 
- **Anonymous by design**: A randomly generated `anonymous_device_id` (in `localStorage`) keys a user's history, minimizing personal data collection.
- **AI Degradation**: The Gemini API is best-effort. If unreachable, the fallback rule engine guarantees the app continues delivering advice.

---

## 8. Evaluation Rubric Mapping

| Axis | Implementation Details |
|------|---------------|
| **Code Quality** | Typed end-to-end (`Pydantic v2` + `TypeScript Strict`). Implements Enterprise Dependency Injection (`app/deps.py`) to decouple Database and AI clients. Pure mathematical functions for CO₂e. `ruff` linter + `mypy` passing CI. |
| **Security** | Security headers middleware (`CSP`, `HSTS`, `X-Frame-Options`). `slowapi` rate-limiting. Bounded `Pydantic` input validation limits. Secrets are excluded from the repository. Non-root user in Docker container. |
| **Efficiency** | Progressive Web App (PWA) with Service Worker offline caching. Slim multi-stage Alpine Docker image. Asynchronous `BackgroundTasks` offload AI generation. Minified frontend bundle. |
| **Testing** | `pytest` backend suite verifying mathematical calculations, endpoint routing, and dependency injection mocks. `vitest` frontend tests. Automated `axe-core` accessibility checks. Fully integrated GitHub Actions CI. |
| **Accessibility** | Screen-reader optimized visually hidden data tables (`.sr-only`) backing Recharts graphs. Skip-to-content links. Bound `<label>` controls. ARIA tablists. `aria-live="polite"` for dynamic AI insights. |
| **Google Services** | Integrates Google Gemini using `google-generativeai==0.8.3`. Leverages `gemini-3.5-flash` for dynamic Eco-Concierge generation, and `gemini-3.1-flash-image` (vision) for automated utility receipt parsing. |
| **Problem Statement Alignment** | Direct alignment with the "Understand → Track → Reduce" loop. Users *Understand* their baseline through calculations, *Track* progress on leaderboards, and *Reduce* emissions via Gemini coaching insights. |
