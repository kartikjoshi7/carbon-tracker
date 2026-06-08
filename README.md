# Smart Campus Sustainability Engine 🌱

A comprehensive, enterprise-grade carbon tracking and sustainability dashboard designed for university students. The application provides instant mathematical $CO_2e$ calculations alongside AI-driven, highly contextual "Eco-Concierge" reduction strategies.

## 🚀 Key Features

*   **Real-time Carbon Tracking:** Accurately calculate your carbon footprint across three core metrics: Energy Usage, Transit Modes, and Meal/Cafeteria Waste.
*   **AI Eco-Concierge Insights:** A hybrid AI engine (powered by Google Gemini) generates personalized reduction strategies. If the API is unavailable, the system intelligently defaults to a robust, rules-based static fallback to guarantee 100% uptime.
*   **Advanced Glassmorphism UI:** A sleek, dark-themed React dashboard utilizing pure Vanilla CSS. Features include deep translucent borders, smooth `translateY` micro-animations, and a centralized `aria-live` insight panel with pulsating skeleton loaders.
*   **Enterprise-Grade Backend Security:** The FastAPI backend is shielded by `slowapi` rate-limiting (enforcing strict limits to prevent DoS attacks) and configured with robust CORS policies.
*   **Non-Blocking Architecture:** High-latency AI generation tasks are safely offloaded to FastAPI `BackgroundTasks`, ensuring instantaneous UI interactions.

## 🛠 Tech Stack

*   **Frontend:** React 18, Vite, TypeScript (Strict Mode), Vanilla CSS
*   **Backend:** Python 3, FastAPI, Pydantic v2, SlowAPI
*   **AI Engine:** Google Generative AI (`gemini-1.5-flash`)
*   **Database Integration:** Supabase (PostgreSQL via Python Client)

## ⚙️ Local Development Setup

To run this application locally, you will need to open two separate terminal windows.

### 1. Backend Server
Navigate to the `backend` directory, activate the virtual environment, install the dependencies, and boot the FastAPI server.

```bash
cd backend
python -m venv venv

# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Boot the API server
python -m uvicorn app.main:app --reload --port 8000
```
*The API will be available at `http://localhost:8000`*

#### Environment Variables
Ensure you have a `.env` file in the `backend/` directory with the following keys:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key  # Optional: Will use static fallback if omitted
```

### 2. Frontend React Client
Navigate to the `frontend` directory, install the Node dependencies, and start the Vite development proxy.

```bash
cd frontend
npm install
npm run dev
```
*The Dashboard will be available at `http://localhost:5173`*

## 📁 Repository Structure

```text
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI Application & Rate Limiting Initialization
│   │   ├── routers/footprint.py    # Endpoint Routing & Background Task Dispatch
│   │   ├── schemas/footprint.py    # Strict Pydantic v2 Data Validation
│   │   └── services/
│   │       ├── carbon_calc.py      # Pure Deterministic Math Logic
│   │       ├── database.py         # Supabase Connection Client
│   │       └── eco_concierge.py    # Hybrid AI Text Generation
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── src/
    │   ├── Dashboard.tsx           # Global State & UI Layout
    │   ├── EnergyForm.tsx          # Energy Tracking Component
    │   ├── TransitForm.tsx         # Transit Tracking Component
    │   ├── WasteForm.tsx           # Waste Tracking Component
    │   └── index.css               # Centralized Glassmorphism Stylesheet
    ├── tsconfig.app.json           # Extreme Strictness TS Config
    └── package.json
```
