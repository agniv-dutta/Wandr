# Musafir Frontend - AI-Powered Travel Planning

A production-quality React + TypeScript + Tailwind CSS frontend for the Musafir travel planning application.

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm/yarn
- The Musafir backend running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

This will start the Vite development server on `http://localhost:5173`.

### Build for Production

```bash
npm run build
npm run preview
```

## ðŸ“ Project Structure

```
frontend/
â”œâ”€â”€ public/
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ api/
â”‚   â”‚   â””â”€â”€ travel.ts              # Axios API client with all backend calls
â”‚   â”œâ”€â”€ components/
â”‚   â”‚   â”œâ”€â”€ layout/
â”‚   â”‚   â”‚   â”œâ”€â”€ Navbar.tsx         # Navigation header
â”‚   â”‚   â”‚   â””â”€â”€ Footer.tsx         # Footer component
â”‚   â”‚   â”œâ”€â”€ home/
â”‚   â”‚   â”‚   â”œâ”€â”€ Hero.tsx           # Hero section with CTA
â”‚   â”‚   â”‚   â””â”€â”€ FeatureCards.tsx   # Feature showcase cards
â”‚   â”‚   â”œâ”€â”€ planner/
â”‚   â”‚   â”‚   â”œâ”€â”€ TripForm.tsx       # Trip planning form
â”‚   â”‚   â”‚   â”œâ”€â”€ ResultPanel.tsx    # Results container with tabs
â”‚   â”‚   â”‚   â”œâ”€â”€ ItineraryTab.tsx   # Day-by-day itinerary view
â”‚   â”‚   â”‚   â”œâ”€â”€ WeatherTab.tsx     # 7-day weather forecast
â”‚   â”‚   â”‚   â”œâ”€â”€ CurrencyTab.tsx    # Currency conversion
â”‚   â”‚   â”‚   â”œâ”€â”€ DestinationTab.tsx # Destination information
â”‚   â”‚   â”‚   â””â”€â”€ AgentTraceTab.tsx  # ReAct agent reasoning trace
â”‚   â”‚   â””â”€â”€ ui/
â”‚   â”‚       â”œâ”€â”€ Button.tsx         # Reusable button component
â”‚   â”‚       â”œâ”€â”€ Card.tsx           # Glassmorphism card
â”‚   â”‚       â”œâ”€â”€ Spinner.tsx        # Loading spinner
â”‚   â”‚       â”œâ”€â”€ Badge.tsx          # Status badges
â”‚   â”‚       â””â”€â”€ TabBar.tsx         # Navigation tabs
â”‚   â”œâ”€â”€ hooks/
â”‚   â”‚   â””â”€â”€ useTripPlanner.ts      # Custom hook for trip planning logic
â”‚   â”œâ”€â”€ pages/
â”‚   â”‚   â”œâ”€â”€ HomePage.tsx           # Home page (/)
â”‚   â”‚   â””â”€â”€ PlannerPage.tsx        # Planner page (/plan)
â”‚   â”œâ”€â”€ types/
â”‚   â”‚   â””â”€â”€ index.ts               # TypeScript interfaces
â”‚   â”œâ”€â”€ App.tsx                    # Main app component with routing
â”‚   â”œâ”€â”€ main.tsx                   # Entry point
â”‚   â””â”€â”€ index.css                  # Tailwind directives
â”œâ”€â”€ index.html
â”œâ”€â”€ package.json
â”œâ”€â”€ tailwind.config.ts
â”œâ”€â”€ tsconfig.json
â”œâ”€â”€ vite.config.ts
â””â”€â”€ postcss.config.js
```

## ðŸŽ¨ Design System

### Colors
- **Primary**: Violet (600) to Indigo (600) gradient
- **Accent**: Amber (400) for highlights
- **Background**: Zinc (950) dark base
- **Surfaces**: Zinc (900/800) for cards
- **Text**: Zinc (50) primary, Zinc (400) secondary

### Typography
- Font: Inter (Google Fonts)
- H1: text-6xl font-black
- H2: text-3xl font-bold
- Body: text-base font-normal
- Code: Monospace with font-mono

### Components Style
- Glassmorphism: `bg-zinc-900/80 backdrop-blur-xl border border-zinc-700/50`
- Rounded corners: 2xl for cards, xl for inputs, full for badges
- Animations: Smooth transitions with Framer Motion
- Dark theme only

## ðŸ”Œ API Integration

The frontend communicates with the backend via Axios at `http://localhost:8000`.

### Available Endpoints

```typescript
// Plan a trip
POST /api/plan
{
  destination: string;
  duration: number;
  budgetAmount: number;
  budgetCurrency: string;
  budgetLevel: 'Budget' | 'Moderate' | 'Luxury';
  travelStyle: string;
  constraints?: string;
}

// Get weather forecast
GET /api/weather?destination=Tokyo

// Convert currency
GET /api/currency?from=INR&to=JPY&amount=150000

// Get destination info
GET /api/destination?name=Tokyo
```

## ðŸ“¦ Dependencies

### Core
- **React 18**: UI framework
- **React Router v6**: Client-side routing
- **Vite**: Build tool and dev server

### Styling
- **Tailwind CSS 3**: Utility-first CSS framework
- **PostCSS**: CSS processing

### Libraries
- **Axios**: HTTP client for API calls
- **Framer Motion**: Animations and interactions
- **Lucide React**: Icon library

## ðŸŽ¬ Key Features

### Pages

#### Home Page (/)
- Hero section with animated gradient orbs
- Feature cards showcasing 4 capabilities
- "How it works" section with visual stepper
- Popular trip examples
- Navigation to planner

#### Planner Page (/plan)
- Left sidebar: Trip planning form with fields:
  - Destination input
  - Duration slider (1-30 days)
  - Budget amount and currency selector
  - Budget level toggle (Budget/Moderate/Luxury)
  - Travel style grid (6 options)
  - Special requirements textarea

- Right panel: Results with 5 tabs:
  - **Itinerary**: Expandable day-by-day plan
  - **Weather**: 7-day forecast with warnings
  - **Currency**: Conversion display and reference table
  - **Destination**: Country information and tips
  - **Agent Trace**: ReAct reasoning steps

### Animations
- Staggered fade-in for hero text
- Scroll-triggered animations for feature cards
- Smooth tab transitions
- Loading skeleton states
- Floating emoji animations

## ðŸ”§ Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

### Tailwind Configuration

Custom colors and animations configured in `tailwind.config.ts`:
- Extended color palette
- Custom animation (float effect)
- Responsive breakpoints (mobile-first)

## ðŸš€ Running Both Frontend and Backend

### Terminal 1: Backend (FastAPI)
```bash
cd backend
pip install fastapi uvicorn pydantic
python -m uvicorn backend.server:app --reload --port 8000
```

### Terminal 2: Frontend (Vite)
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

## ðŸ“± Responsive Design

- **Mobile** (<640px): Single column, stacked components
- **Tablet** (640-1024px): 2-column feature cards
- **Desktop** (>1024px): Full 2-column planner layout, all features visible

## ðŸŽ¨ Customization

### Change Primary Colors
Edit `tailwind.config.ts`:
```typescript
extend: {
  colors: {
    violet: { ... },  // Modify here
    indigo: { ... }
  }
}
```

### Modify Form Fields
Edit `src/components/planner/TripForm.tsx` to add/remove fields

### Add New Tabs
1. Create new component in `src/components/planner/`
2. Add to `ResultPanel.tsx` tabs array
3. Add AnimatePresence case

## ðŸ› Debugging

### API Errors
- Check backend is running on port 8000
- Check browser console for error messages
- Use browser DevTools Network tab to inspect API calls
- Check `.env` file has correct `VITE_API_URL`

### Styling Issues
- Ensure Tailwind classes are used consistently
- Clear browser cache if styles don't update
- Check tailwind.config.ts for custom configuration

### Component Issues
- React DevTools browser extension helps inspect props
- Check TypeScript types in `src/types/index.ts`
- Verify all imports are correct

## ðŸ“ Notes

- All components are fully functional with no placeholder code
- TypeScript strict mode is enabled for type safety
- Fallback data provided if backend endpoints crash
- Responsive design tested on mobile, tablet, and desktop
- Animations use Framer Motion for smooth performance

## ðŸ¤ Backend Integration

The frontend expects the backend to provide:

1. **Agent execution** with intermediate steps
2. **Weather API** integration via tool
3. **Currency conversion** with live rates
4. **Destination information** lookup
5. **Itinerary generation** based on preferences

If running without the full LangChain agent, the `backend/server.py` provides mock data fallbacks.

## ðŸ“š Additional Resources

- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Framer Motion](https://www.framer.com/motion/)
- [Axios](https://axios-http.com)
- [Vite](https://vitejs.dev)

---

Built with â¤ï¸ for the Musafir travel planning platform.

