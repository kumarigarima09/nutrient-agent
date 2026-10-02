# Nutrient Agent — Everyday Food Support & AI Nutrition Companion 🥗

> **Practical, personal, pressure-free food guidance built on deterministic, science-backed nutritional calculations.**

Inspired by modern editorial aesthetics with a warm linen palette, terracotta action accents, and sage indicators, **Nutrient Agent** combines deterministic metabolic modeling (Mifflin-St Jeor, WHO macronutrient splits, TDEE) with an evidence-grounded AI agent, natural language food logging, 7-day meal planning, and automated supermarket grocery aggregation.

---

## 🌟 Key Features

### 1. 📊 Deterministic Metabolic & Target Engine
- **Calculations**: Precision Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE) based on age, sex, weight, height, and activity level.
- **Macronutrient Splits**: Scientifically balanced protein, carb, and fat goals adjusted for weight loss, maintenance, or muscle gain.
- **Micro-Targeting**: Daily water intake, minimum daily fiber benchmarks, and caloric targets.

### 2. 📅 7-Day Weekly Meal Scheduling & Smart Plan Feed
- **Dynamic Weekly Feed**: Generates a varied 7-day meal plan (Breakfast, Lunch, Evening Snack, Dinner) tailored to cultural dietary preferences (Vegetarian, Non-Vegetarian, Vegan, Eggetarian).
- **Macro Breakdowns per Day & Meal**: Every meal card displays exact calorie counts, grams of protein, portion sizes, and preparation tips.
- **Instant Logging**: One-click logging from planned meal slots directly into today's food intake log.

### 3. 🛒 Aggregated Supermarket Grocery Hauls
- **Automated Aggregation**: Traverses the entire 7-day meal plan and tallies raw ingredient quantities.
- **Aisle Categorization**: Automatically groups ingredients into store aisles (Fresh Produce, Dairy & Protein, Grains & Staples, Nuts & Snacks, Spices & Pantry).
- **Checklist Persistence**: Interactive check-off system saved locally in `localStorage` for stress-free grocery shopping.

### 4. 💬 Grounded AI Nutrition Coach & Chat
- **RAG & Tool Calling**: Answers questions grounded in verified nutritional science and Indian food composition data (IFCT / USDA).
- **Context-Aware Recommendations**: Offers practical meal substitutions, macro adjustments, and pressure-free habit coaching.

### 5. ⚡ Natural Language Food Logging & Image Analysis
- **Smart Parsing**: Type natural meals like *"2 rotis with paneer sabzi and 1 cup curd"* and automatically resolve matched items, portion grams, calories, and macros.
- **Quick Logging Chips**: One-tap logging for common daily items.
- **Visual Food Analysis**: Upload food photos for automatic nutrient breakdown suggestions.

---

## 🛠️ Architecture & Tech Stack

```
                                  ┌───────────────────────────┐
                                  │      React + Vite UI      │
                                  │  (DM Sans, Fraunces Serif │
                                  │   Linen/Terracotta Theme) │
                                  └─────────────┬─────────────┘
                                                │ REST API / JSON
                                                ▼
                                  ┌───────────────────────────┐
                                  │      FastAPI Backend      │
                                  │ (Uvicorn, Pydantic, Auth) │
                                  └──────┬─────────────┬──────┘
                                         │             │
                    ┌────────────────────┴──┐       ┌──┴────────────────────┐
                    │  Deterministic Logic  │       │     Data & Storage    │
                    ├───────────────────────┤       ├───────────────────────┤
                    │ • NutritionCalculator │       │ • SQLite (SQLAlchemy) │
                    │ • MealPlanner (7-Day) │       │ • RAG Vector Embeds   │
                    │ • FoodLogger (NLP)    │       │ • Indian Food DB      │
                    │ • Safety / Feasibility│       │ • User Profile & Logs │
                    └───────────────────────┘       └───────────────────────┘
```

- **Frontend**: React 18, TypeScript, Vite, TailwindCSS v4, Lucide Icons, Canvas Confetti.
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2, SQLite (PostgreSQL compatible).
- **Security**: JWT Authentication (python-jose), bcrypt password hashing.

---

## 🚀 Local Quickstart

### Prerequisites
- Node.js (v18+ recommended)
- Python (3.10+ recommended)

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```
Backend will be live at `http://localhost:8000` (API docs at `http://localhost:8000/docs`).

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be running at `http://localhost:5173`.

### 3. Demo Credentials
- **Email**: `demo@nutritionagent.ai`
- **Password**: `demo1234`

---

## 🌐 Deployment Guide (Vercel & Cloud)

### Frontend Deployment on Vercel

1. **Option A: Vercel CLI (Recommended)**
   ```bash
   cd frontend
   npm run build
   npx vercel
   ```
2. **Option B: GitHub / Vercel Web Dashboard**
   - Import your repository on [vercel.com](https://vercel.com).
   - Set **Root Directory** to `frontend` (or keep root with `vercel.json` already provided in the repository).
   - Set **Framework Preset** to `Vite`.
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Environment Variables on Vercel**:
   Add the following under **Project Settings > Environment Variables**:
   ```ini
   VITE_API_URL=https://your-backend-service.onrender.com
   ```
   *(If not set, the frontend defaults to `/api` proxy rewrites configured in `vercel.json`)*.

---

### Backend Deployment (Render / Railway / Fly.io / Docker)

The FastAPI backend is fully container-ready and WSGI/ASGI compatible.

#### Deploying on Render / Railway:
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Root Directory**: `backend`
- **Environment Variables**:
  ```ini
  SECRET_KEY=your-secure-random-secret-key-32-chars-minimum
  ENVIRONMENT=production
  DATABASE_URL=sqlite:///./nutrition.db  # Or postgresql://user:pass@host/dbname
  ```

---

## 🧪 Testing

### Backend Unit & Integration Tests
```bash
cd backend
PYTHONPATH=. pytest
```
*Current test suite: 19 unit & endpoint test cases passing.*

### Frontend Production Build Validation
```bash
cd frontend
npm run build
```

---

## 📁 Repository Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routers (auth, meal_plan, food_log, chat, etc.)
│   │   ├── core/            # Config, database setup, JWT security
│   │   ├── models/          # SQLAlchemy DB models (User, Profile, MealPlan, etc.)
│   │   ├── schemas/         # Pydantic validation schemas
│   │   └── services/        # MealPlanner, NutritionCalculator, FoodLogger, RAG
│   ├── tests/               # Pytest automated test suites
│   ├── requirements.txt     # Backend dependencies
│   └── nutrition.db         # Pre-seeded SQLite database
├── frontend/
│   ├── src/
│   │   ├── api/             # Typed API client with VITE_API_URL support
│   │   ├── components/      # MacroRing, WeightChart, QuickLog, AppShell
│   │   ├── pages/           # Dashboard, MealPlan, Chat, FoodLog, Progress, Auth
│   │   └── index.css        # Warm linen, terracotta, and editorial design system
│   ├── package.json         # Frontend packages
│   ├── vercel.json          # SPA routing rewrites for Vercel
│   └── vite.config.ts       # Vite configuration with proxying
├── vercel.json              # Root Vercel deployment configuration
└── README.md                # Project documentation
```

---

## 📄 License
MIT License. Built for modern, evidence-grounded everyday nutrition support.
