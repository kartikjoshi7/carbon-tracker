# Smart Campus Sustainability Engine 🌱

> **Challenge Vertical:** [Challenge 3] Carbon Footprint Awareness Platform  
> *Design a solution that helps individuals understand, track, and reduce their carbon footprint through simple actions and personalized insights.*

---

## 🎯 Chosen Vertical

**Carbon Footprint Awareness Platform** — This project tackles Challenge 3 by providing a complete, end-to-end carbon tracking and reduction system tailored to university students. It combines deterministic mathematical CO₂e calculations with AI-generated personalized reduction strategies to create a smart, dynamic assistant that drives real behavioral change.

---

## 🧠 Approach and Logic

### Architecture
The application follows a **decoupled monorepo** architecture with a FastAPI backend and a React (Vite) frontend:

```
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
│  Glassmorphism   │                     │  │ Eco-Concierge  │   │
│  PWA             │                     │  │ (Gemini + FB)  │   │
└─────────────────┘                     │  ├────────────────┤   │
                                        │  │ Supabase DB    │   │
                                        │  └────────────────┘   │
                                        └──────────────────────┘
```

### Core Decision-Making Logic
1. **Deterministic Math Engine** (`carbon_calc.py`): Pure functions calculate CO₂e using established emission factors:
   - Energy: `((ac_hours × 1.5 × 0.82) / roommates) + ((shared_kwh × 0.82) / roommates)`
   - Transit: `(distance × mode_factor) / passengers` — factors: rickshaw=0.05, shuttle=0.02, two_wheeler=0.10, walking=0.0
   - Waste: `grams × 0.002`

2. **Hybrid AI Engine** (`eco_concierge.py`): Attempts Gemini 1.5 Flash for contextual tips. If the API key is missing or the call fails, it seamlessly falls back to a static rules-based generator matching the university student persona — guaranteeing **100% uptime** with zero crashes.

3. **Non-Blocking Architecture**: The API returns calculated CO₂e scores **instantly**. Heavy AI text generation is offloaded to `FastAPI.BackgroundTasks`, ensuring the UI never waits for the LLM.

---

## ⚙️ How the Solution Works

### For the User
1. **Track** — Open the dashboard. Select a category (Energy, Transit, or Waste). Fill in your daily metrics and click "Track." You instantly see your CO₂e score.
2. **Learn** — The AI Eco-Concierge panel at the bottom generates a personalized reduction tip (e.g., "Split AC costs with roommates to save X kg CO₂e").
3. **Analyze** — Switch to the "Data Analytics" tab to view interactive Pie Charts and Bar Graphs of your historical emissions breakdown.
4. **Compete** — The "Leaderboard" tab ranks all platform users by lowest total CO₂e footprint, encouraging friendly competition.
5. **Upload** — Use the AI Receipt Parser to upload a photo of an electricity bill or transit receipt. Gemini Vision extracts the values and auto-fills the form.
6. **Install** — The dashboard is a Progressive Web App (PWA). Students can install it on their phones for native-like access.

### Running Locally

**Backend:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate        # Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Running Tests:**
```bash
cd backend
.\venv\Scripts\python -m pytest tests/ -v
```

### Environment Variables
Create a `backend/.env` file:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
GEMINI_API_KEY=your_gemini_api_key   # Optional — static fallback activates if omitted
```

---

## 📋 Assumptions Made

1. **Target Persona**: A generic "university student living in a shared off-campus apartment." No specific city, state, or institution names are used.
2. **Emission Factors**: Simplified CO₂e conversion factors (e.g., 0.82 kg CO₂/kWh for India's average grid) are used for demonstration. In production, these would be sourced from region-specific government databases.
3. **User Identity**: A placeholder `user_id = "user_123"` is used for all tracking. In production, this would be replaced with a proper authentication system (e.g., Supabase Auth).
4. **Supabase Table Creation**: The `supabase_schema.sql` file in the repo root contains the SQL to create the required tables. If the tables don't exist, the backend gracefully serves mock data for demonstration.
5. **AI Availability**: The Gemini API key is optional. The static fallback generator ensures the app never crashes during automated testing or evaluation, even without network access.

---

## 🧪 Testing

The project includes **37 automated tests** covering:
- **22 Unit Tests** — Validate all 3 CO₂e calculation functions with edge cases, boundary values, zero inputs, type checks, and precision verification.
- **15 Integration Tests** — Validate all 6 FastAPI endpoints using `TestClient`, including Pydantic validation error handling (422 responses for invalid inputs).

```
============================= 37 passed in 6.12s =============================
```

---

## 🔐 Security

- **Rate Limiting**: `slowapi` enforces 10 requests/minute globally.
- **Input Validation**: Strict Pydantic v2 `Field` constraints with `ge`, `le`, and `Literal` types.
- **CORS**: Restricted to explicit localhost origins only.
- **Environment Variables**: All secrets stored in `.env` (excluded via `.gitignore`).
- **Error Handling**: Every database and AI call is wrapped in `try-except` blocks with structured logging.

---

## ♿ Accessibility

- All form inputs have proper `<label htmlFor>` / `<input id>` bindings for screen readers.
- Tab navigation uses `role="tablist"` and `role="tab"` with `aria-selected` attributes.
- The AI insight panel uses `aria-live="polite"` for dynamic content updates.
- All interactive buttons include `aria-busy` states during loading.
- Semantic HTML5 elements (`<main>`, `<header>`, `<section>`, `<nav>`, `<form>`) are used throughout.

---

## 🛠 Tech Stack

| Layer      | Technology                                    |
|------------|-----------------------------------------------|
| Frontend   | React 18, Vite, TypeScript (Strict), Recharts |
| Styling    | Vanilla CSS (Glassmorphism, no Tailwind)       |
| Backend    | Python 3.12, FastAPI, Pydantic v2, SlowAPI     |
| AI Engine  | Google Gemini 1.5 Flash + Static Fallback      |
| Database   | Supabase (PostgreSQL)                          |
| PWA        | vite-plugin-pwa                                |
| Testing    | pytest, FastAPI TestClient, httpx              |
