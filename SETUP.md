# Wandr - Complete Setup Guide

A production-quality AI-powered travel planning application with a React + TypeScript + Tailwind CSS frontend and Python FastAPI backend.

## 📋 Project Overview

**Wandr** is an intelligent trip planner that combines:
- 🎨 Modern, responsive React frontend
- ⚙️ Python backend with LangChain agent integration
- 🌐 Real API integration for weather, currency, and destination data
- ✨ Beautiful dark theme with glassmorphism design
- 🎬 Smooth animations with Framer Motion

## ⚙️ System Requirements

- **Node.js**: 16.x or higher
- **npm**: 8.x or higher  
- **Python**: 3.9 or higher
- **pip**: Python package manager

## 🚀 Quick Start (5 minutes)

### Step 1: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 2: Install Backend Dependencies

```bash
cd backend
pip install fastapi uvicorn pydantic
```

### Step 3: Run Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn server:app --reload --port 8000
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

You should see:
```
  ➜  Local:   http://localhost:5173/
```

### Step 4: Open in Browser

Visit `http://localhost:5173` and start planning trips!

---

## 📚 Detailed Setup Instructions

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd frontend
```

#### 2. Install Dependencies
```bash
npm install
```

This installs:
- React & React DOM
- React Router for navigation
- Axiosfor HTTP requests
- Framer Motion for animations
- Tailwind CSS for styling
- TypeScript for type safety
- Vite for fast development server

#### 3. Create Environment File (Optional)
```bash
cp .env.example .env
```

Edit `.env` if needed (default should work):
```env
VITE_API_URL=http://localhost:8000
```

#### 4. Start Development Server
```bash
npm run dev
```

The app will open at `http://localhost:5173`

#### 5. Build for Production
```bash
npm run build
npm run preview
```

### Backend Setup

#### 1. Navigate to Backend Directory
```bash
cd backend
```

#### 2. Install Dependencies
```bash
pip install fastapi uvicorn pydantic
```

Additional packages if using the full LangChain agent:
```bash
pip install langchain groq
```

#### 3. Start the Server
```bash
python -m uvicorn server:app --reload --port 8000
```

Server runs at `http://localhost:8000`

#### 4. Test the API
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

---

## 🏗️ Architecture

### Frontend Architecture

```
Frontend (React + TypeScript + Tailwind)
├── Pages
│   ├── HomePage (/)
│   └── PlannerPage (/plan)
├── Components
│   ├── Layout (Navbar, Footer)
│   ├── Home (Hero, FeatureCards)
│   └── Planner (Form, ResultPanel, Tabs)
├── Hooks
│   └── useTripPlanner (state management)
├── API
│   └── travel.ts (Axios client)
└── Types (TypeScript interfaces)
```

### Backend Architecture

```
Backend (FastAPI)
├── POST /api/plan (Main agent endpoint)
├── GET /api/weather (Weather forecast)
├── GET /api/currency (Currency conversion)
└── GET /api/destination (Destination info)
```

---

## 🎯 Frontend Features

### Home Page (/)
- **Hero Section**: Animated gradient orbs, main CTA
- **Feature Cards**: 4 key capabilities with icons
- **How It Works**: Visual 3-step process
- **Popular Trips**: Example destinations
- **Responsive**: Mobile, tablet, desktop optimized

### Planner Page (/plan)
- **Trip Form** (Left sidebar):
  - Destination input with icon
  - Duration slider (1-30 days)
  - Budget amount + currency selector
  - Budget level toggle (Budget/Moderate/Luxury)
  - Travel style grid (6 interactive options)
  - Special requirements textarea

- **Result Panel** (Right side):
  - 5 tabbed views:
    1. **Itinerary**: Day-by-day expandable plan
    2. **Weather**: 7-day forecast with weather warnings
    3. **Currency**: Conversion display + reference table
    4. **Destination**: Country info, languages, tips
    5. **Agent Trace**: ReAct reasoning steps
  - Download plan button
  - New trip button

### UI Components
- Custom `Button` with variants (primary, secondary, ghost)
- `Card` with glassmorphism styling
- `Spinner` for loading states
- `Badge` for tags and status
- `TabBar` for tab navigation
- All fully accessible and responsive

---

## 🎨 Design System

### Color Palette
```
Primary:    Violet (600) → Indigo (600) gradient
Accent:     Amber (400)
Background: Zinc (950) - dark
Surface:    Zinc (900/800)
Text:       Zinc (50) / Zinc (400) / Zinc (600)
Success:    Emerald (400)
Warning:    Amber (400)
Error:      Red (400)
```

### Typography
- **Font**: Inter (via Google Fonts)
- **H1**: text-6xl font-black
- **H2**: text-3xl font-bold  
- **Body**: text-base font-normal
- **Code**: font-mono text-sm

### Components Style
- **Glassmorphism**: `bg-zinc-900/80 backdrop-blur-xl border border-zinc-700/50`
- **Rounded**: 2xl for cards, xl for inputs, full for badges
- **Shadows**: Subtle with hover effect `shadow-lg shadow-violet-500/20`
- **Animations**: Framer Motion with smooth easing

---

## 🔌 API Specification

### 1. Plan Trip
**POST** `/api/plan`

Request:
```json
{
  "destination": "Tokyo",
  "duration": 5,
  "budgetAmount": 500000,
  "budgetCurrency": "INR",
  "budgetLevel": "Moderate",
  "travelStyle": "Cultural",
  "constraints": "Vegetarian, kids friendly"
}
```

Response:
```json
{
  "final_answer": "Day 1: ...",
  "intermediate_steps": [
    {
      "tool": "destination_tool",
      "input": "{...}",
      "output": "{...}"
    },
    ...
  ]
}
```

### 2. Weather Forecast
**GET** `/api/weather?destination=Tokyo`

Response:
```json
{
  "forecast": [
    {
      "date": "2024-04-02",
      "condition": "Clear",
      "maxTemp": 25,
      "minTemp": 18,
      "precipitation": 0,
      "windSpeed": 12,
      "weatherCode": 1000
    },
    ...
  ],
  "recommendation": "Perfect weather for outdoor activities"
}
```

### 3. Currency Conversion
**GET** `/api/currency?from=INR&to=JPY&amount=500000`

Response:
```json
{
  "converted": 3450000,
  "rate": 6.9,
  "updated": "2024-04-02T10:30:00",
  "from": "INR",
  "to": "JPY",
  "amount": 500000
}
```

### 4. Destination Info
**GET** `/api/destination?name=Tokyo`

Response:
```json
{
  "country": "Japan",
  "capital": "Tokyo",
  "population": "37.4 million",
  "timezone": "JST (UTC+9)",
  "currency": "JPY",
  "languages": ["Japanese"],
  "coordinates": {
    "latitude": 35.6762,
    "longitude": 139.6503
  },
  "tips": [
    "Use the extensive train system",
    "Cash is still widely used",
    ...
  ]
}
```

---

## 📁 File Structure

```
Wandr/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   └── Footer.tsx
│   │   │   ├── home/
│   │   │   │   ├── Hero.tsx
│   │   │   │   └── FeatureCards.tsx
│   │   │   ├── planner/
│   │   │   │   ├── TripForm.tsx
│   │   │   │   ├── ResultPanel.tsx
│   │   │   │   ├── ItineraryTab.tsx
│   │   │   │   ├── WeatherTab.tsx
│   │   │   │   ├── CurrencyTab.tsx
│   │   │   │   ├── DestinationTab.tsx
│   │   │   │   └── AgentTraceTab.tsx
│   │   │   └── ui/
│   │   │       ├── Button.tsx
│   │   │       ├── Card.tsx
│   │   │       ├── Spinner.tsx
│   │   │       ├── Badge.tsx
│   │   │       └── TabBar.tsx
│   │   ├── hooks/
│   │   │   └── useTripPlanner.ts
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   └── PlannerPage.tsx
│   │   ├── api/
│   │   │   └── travel.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── .env
│   └── README.md
├── backend/
│   ├── server.py          (FastAPI main server)
│   ├── agent_core.py      (LangChain agent)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── weather_tool.py
│   │   ├── currency_tool.py
│   │   ├── destination_tool.py
│   │   └── itinerary_tool.py
│   └── requirements.txt
├── tools/                 (Shared tools directory)
└── README.md
```

---

## 🐛 Troubleshooting

### Frontend Errors

**Issue**: `Port 5173 already in use`
```bash
npm run dev -- --port 5174
```

**Issue**: Modules not found
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Issue**: Styles not loading
```bash
# Clear Tailwind cache
npm run build
```

### Backend Errors

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
pip install fastapi uvicorn pydantic
```

**Issue**: `Port 8000 already in use`
```bash
python -m uvicorn server:app --reload --port 8001
```

**Issue**: CORS errors
- Ensure backend CORS is configured for frontend URL
- Check `server.py` CORSMiddleware settings

### Connection Issues

**Frontend can't reach backend**:
1. Verify backend is running on `http://localhost:8000`
2. Check `.env` file has correct `VITE_API_URL`
3. Check browser console for error messages
4. Verify ports: Frontend (5173), Backend (8000)

---

## 🚢 Deployment

### Frontend Deployment (Vercel/Netlify)

1. Build the project:
```bash
cd frontend
npm run build
```

2. Deploy the `dist` folder to your hosting provider

3. Set environment variable:
```
VITE_API_URL=https://your-backend-url.com
```

### Backend Deployment (Heroku/Railway/Digital Ocean)

1. Create `requirements.txt` in backend:
```bash
pip freeze > requirements.txt
```

2. Deploy using your platform's CLI

3. Set environment variables if needed

---

## 📝 Key Features Implemented

✅ Responsive design (mobile, tablet, desktop)
✅ Dark theme with glassmorphism
✅ Smooth animations with Framer Motion
✅ Full TypeScript type safety
✅ Custom form validation
✅ Error handling and fallbacks
✅ Tab navigation with smooth transitions
✅ Weather forecast with warnings
✅ Currency conversion with reference table
✅ Destination information display
✅ Agent reasoning trace visualization
✅ Download trip plan feature
✅ Loading skeleton states
✅ Real-time status updates
✅ Mobile menu navigation

---

## 🎓 Learning Resources

- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Framer Motion](https://www.framer.com/motion/)
- [React Router](https://reactrouter.com/en/main)
- [Axios Documentation](https://axios-http.com/docs/intro)
- [FastAPI](https://fastapi.tiangolo.com/)

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review frontend/README.md for detailed component info
3. Check browser console for error messages
4. Verify both servers are running

---

## 📄 License

This project is part of the Wandr travel planning platform.

---

**Happy traveling with Wandr! ✈️**
