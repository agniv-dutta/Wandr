import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from datetime import datetime, timedelta
import random
import sys
import os
import requests
from dotenv import load_dotenv

# Add the parent directory to the path to import agent_core
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

# Load environment variables from repo root .env, fallback to backend/env
root_env = os.path.join(ROOT_DIR, ".env")
backend_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), "env")
if os.path.exists(root_env):
    load_dotenv(root_env)
elif os.path.exists(backend_env):
    load_dotenv(backend_env)
else:
    load_dotenv()

app = FastAPI(title="Wandr API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================

class TripRequest(BaseModel):
    destination: str
    origin: Optional[str] = None
    duration: int
    budgetAmount: float
    budgetCurrency: str
    budgetLevel: str
    travelStyle: str
    constraints: Optional[str] = None

class CalendarEvent(BaseModel):
    day: int
    title: str
    time: str
    description: Optional[str] = ""

class CalendarExportRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    events: List[CalendarEvent] = []

class TransportRequest(BaseModel):
    origin: str
    destination: str
    date: str
    modes: List[str]

class FoodRequest(BaseModel):
    city: str
    country: Optional[str] = ""
    days: int
    budget_level: str

class BudgetRequest(BaseModel):
    destination: str
    origin: str
    start_date: str
    end_date: str
    travelers: int
    budget_level: str

class WeatherDay(BaseModel):
    date: str
    condition: str
    maxTemp: float
    minTemp: float
    precipitation: float
    windSpeed: float
    weatherCode: int

class IntermediateStep(BaseModel):
    tool: str
    input: str
    output: str

class TripResponse(BaseModel):
    final_answer: str
    intermediate_steps: list[IntermediateStep]

class DestinationRequest(BaseModel):
    name: str


class BudgetBreakdownRequest(BaseModel):
    destination: str
    origin: Optional[str] = ""
    duration: int
    budgetAmount: float
    budgetCurrency: str
    budgetLevel: str
    departureDate: str
    adults: int = 1


class PlaceSuggestion(BaseModel):
    name: str
    display_name: str
    city: str = ""
    country: str = ""
    type: str = ""

# ==================== HELPER FUNCTIONS ====================

def generate_sample_itinerary(destination: str, duration: int, budget_level: str, travel_style: str) -> str:
    """Generate a sample itinerary for demonstration"""
    activities = {
        "Cultural": [
            "Visit historical temples and museums",
            "Take a guided cultural tour",
            "Experience local heritage sites",
            "Attend traditional performances"
        ],
        "Beach": [
            "Relax on pristine beaches",
            "Water sports and snorkeling",
            "Sunset beach walks",
            "Beach clubs and dining"
        ],
        "Adventure": [
            "Hiking and trekking",
            "Rock climbing or mountaineering",
            "Adventurous outdoor activities",
            "Nature exploration"
        ],
        "Food & Nightlife": [
            "Visit local restaurants and street food",
            "Wine or craft beer tasting",
            "Nightlife and entertainment",
            "Cooking classes"
        ],
        "Shopping": [
            "Explore local markets",
            "Visit shopping malls",
            "Boutique browsing",
            "Souvenir shopping"
        ],
        "Balanced": [
            "Mix of cultural, adventure, and relaxation",
            "Explore local attractions",
            "Enjoy local cuisine",
            "Photography and scenic viewpoints"
        ]
    }

    budget_estimates = {
        "Budget": {"low": 30, "high": 50},
        "Moderate": {"low": 50, "high": 100},
        "Luxury": {"low": 150, "high": 300}
    }

    style_activities = activities.get(travel_style, activities["Balanced"])
    budget_range = budget_estimates.get(budget_level, budget_estimates["Moderate"])

    itinerary = f"# {duration}-Day {destination} Itinerary ({travel_style} Travel)\n\n"

    for day in range(1, duration + 1):
        itinerary += f"## Day {day}:\n"
        activities_sample = random.sample(style_activities, min(3, len(style_activities)))
        for activity in activities_sample:
            itinerary += f"- {activity}\n"
        itinerary += "\n"

    itinerary += f"## Budget Summary ({budget_level} Level):\n"
    itinerary += f"- Accommodation: ${budget_range['low'] * duration // 3:.0f} (${budget_range['low']}/night)\n"
    itinerary += f"- Food: ${budget_range['high'] * duration // 3:.0f} (${budget_range['high'] / 3:.0f}/day)\n"
    itinerary += f"- Activities: ${budget_range['high'] * duration // 3:.0f}\n"
    itinerary += f"- **Total: ${(budget_range['low'] + budget_range['high']) * duration:.0f}**\n"

    return itinerary


def _normalize_country_label(destination: str) -> str:
    known = {
        "india": "India",
        "thailand": "Thailand",
        "indonesia": "Indonesia",
        "france": "France",
        "japan": "Japan",
        "uk": "UK",
        "united kingdom": "UK",
        "usa": "USA",
        "united states": "USA",
        "australia": "Australia",
        "singapore": "Singapore",
        "uae": "UAE",
        "dubai": "UAE",
    }

    value = (destination or "").strip().lower()
    if value in known:
        return known[value]

    # Common city -> country hints
    city_to_country = {
        "mumbai": "India",
        "delhi": "India",
        "bangalore": "India",
        "chennai": "India",
        "pune": "India",
        "goa": "India",
        "tokyo": "Japan",
        "kyoto": "Japan",
        "osaka": "Japan",
        "paris": "France",
        "london": "UK",
        "new york": "USA",
        "los angeles": "USA",
        "sydney": "Australia",
        "melbourne": "Australia",
        "bangkok": "Thailand",
        "bali": "Indonesia",
        "jakarta": "Indonesia",
        "singapore city": "Singapore",
        "singapore": "Singapore",
    }

    return city_to_country.get(value, "default")


def _convert_amount_safe(from_currency: str, to_currency: str, amount: float) -> float:
    if from_currency.upper() == to_currency.upper():
        return float(amount)

    try:
        from backend.tools.currency_tool import convert_amount
        converted = convert_amount(from_currency.upper(), to_currency.upper(), float(amount))
        value = converted.get("converted", 0.0)
        return float(value) if value else float(amount)
    except Exception:
        return float(amount)


def _estimate_flight_fallback_inr(origin: str, destination: str) -> int:
    o = (origin or "").strip().lower()
    d = (destination or "").strip().lower()

    india = {"mumbai", "delhi", "bangalore", "chennai", "kolkata", "hyderabad", "pune", "goa", "ahmedabad"}
    if o in india and d in india:
        return 8500

    long_haul = {"new york", "london", "paris", "tokyo", "sydney", "los angeles", "toronto"}
    if o in long_haul or d in long_haul:
        return 52000

    return 28000

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Wandr API is running"}

@app.post("/api/plan")
async def plan_trip(request: TripRequest):
    """Main endpoint to plan a trip using the agent"""
    try:
        # Try to use the actual agent if available
        try:
            from backend.agent_core import agent_executor
            query = f"""
            Plan a {request.duration}-day trip to {request.destination}.
            My budget is {request.budgetAmount} {request.budgetCurrency} ({request.budgetLevel} level).
            Travel style: {request.travelStyle}.
            Special requirements: {request.constraints or 'none'}.
            Origin city: {request.origin or 'not provided'}.
            Convert my budget to local currency, check the weather, and create a detailed itinerary.
            """
            
            result = agent_executor.invoke({"messages": [("user", query)]})

            final_answer = result.get("output", "")
            messages = result.get("messages", [])
            if not final_answer and messages:
                last_message = messages[-1]
                final_answer = getattr(last_message, "content", str(last_message))

            intermediate_steps = [
                IntermediateStep(
                    tool=step[0].tool,
                    input=str(step[0].tool_input),
                    output=str(step[1])
                )
                for step in result.get("intermediate_steps", [])
            ]

            itinerary_step = next(
                (step for step in intermediate_steps if "generate_itinerary" in step.tool),
                None
            )
            if itinerary_step and itinerary_step.output:
                final_answer = itinerary_step.output

            return TripResponse(
                final_answer=final_answer,
                intermediate_steps=intermediate_steps
            )
        except ImportError:
            # Fallback to sample data if agent_core is not available
            itinerary = generate_sample_itinerary(
                request.destination,
                request.duration,
                request.budgetLevel,
                request.travelStyle
            )
            
            intermediate_steps = [
                IntermediateStep(
                    tool="destination_tool",
                    input=json.dumps({"destination": request.destination}),
                    output=json.dumps({
                        "country": request.destination,
                        "currency": "JPY" if "Tokyo" in request.destination else "EUR",
                    })
                ),
                IntermediateStep(
                    tool="weather_tool",
                    input=json.dumps({"destination": request.destination}),
                    output=json.dumps({"forecast": "7-day forecast data"})
                ),
                IntermediateStep(
                    tool="currency_tool",
                    input=json.dumps({"from": request.budgetCurrency, "to": "USD", "amount": request.budgetAmount}),
                    output=json.dumps({"converted": request.budgetAmount * 0.012, "rate": 0.012})
                ),
                IntermediateStep(
                    tool="itinerary_tool",
                    input=json.dumps({"destination": request.destination, "duration": request.duration}),
                    output=itinerary
                ),
            ]
            
            return TripResponse(
                final_answer=itinerary,
                intermediate_steps=intermediate_steps
            )
    
    except Exception as e:
        print(f"/api/plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/weather")
async def get_weather(destination: str):
    """Get weather forecast for a destination"""
    try:
        # Try to use the actual weather tool if available
        try:
            from backend.tools.weather_tool import get_weather_forecast
            data = get_weather_forecast.run(destination)
            forecast = []
            for line in data.split("\n"):
                if ":" not in line:
                    continue
                date_part, rest = line.split(":", 1)
                if "Max" not in rest or "Min" not in rest:
                    continue
                try:
                    condition_part, details = rest.split(",", 1)
                    max_part = details.split("Max")[1].split("/ Min")[0].strip().replace("°C", "")
                    min_part = details.split("/ Min")[1].split(",")[0].strip().replace("°C", "")
                    rain_part = details.split("Rain")[1].split("mm")[0].strip()
                    wind_part = details.split("Wind")[1].split("km/h")[0].strip()
                    forecast.append({
                        "date": date_part.strip(),
                        "condition": condition_part.strip().strip(","),
                        "maxTemp": float(max_part),
                        "minTemp": float(min_part),
                        "precipitation": float(rain_part),
                        "windSpeed": float(wind_part),
                        "weatherCode": 0,
                    })
                except Exception:
                    continue

            return {
                "forecast": forecast,
                "recommendation": "Check daily updates for packing advice.",
            }
        except ImportError:
            # Fallback to sample weather data
            base_date = datetime.now()
            forecast = []
            
            for i in range(7):
                date = base_date + timedelta(days=i)
                forecast.append({
                    "date": date.isoformat(),
                    "condition": random.choice(["Clear", "Cloudy", "Rainy", "Partly Cloudy"]),
                    "maxTemp": random.randint(20, 35),
                    "minTemp": random.randint(10, 20),
                    "precipitation": random.randint(0, 10),
                    "windSpeed": random.randint(5, 25),
                    "weatherCode": random.randint(1000, 9999),
                })
            
            return {
                "forecast": forecast,
                "recommendation": "Pack light clothing and rain gear just in case."
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/currency")
async def convert_currency(from_currency: str = Query("INR", alias="from"), to_currency: str = Query("USD", alias="to"), amount: float = Query(100)):
    """Convert currency"""
    try:
        
        # Try to use the actual currency tool if available
        try:
            from backend.tools.currency_tool import convert_amount
            data = convert_amount(from_currency, to_currency, amount)
            return data
        except ImportError:
            # Fallback to sample currency data
            rates = {
                ("INR", "USD"): 0.012,
                ("INR", "EUR"): 0.011,
                ("INR", "GBP"): 0.0095,
                ("INR", "JPY"): 1.8,
                ("USD", "INR"): 83.33,
                ("EUR", "USD"): 1.09,
            }
            
            rate = rates.get((from_currency, to_currency), 1.0)
            converted = amount * rate
            
            return {
                "converted": converted,
                "rate": rate,
                "updated": datetime.now().isoformat()
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/destination")
async def get_destination(name: str):
    """Get destination information"""
    try:
        # Try to use the actual destination tool if available
        try:
            from backend.tools.destination_tool import get_destination_info
            raw = get_destination_info.run(name)
            parsed = {
                "country": name,
                "capital": name,
                "population": "Unknown",
                "timezone": "UTC",
                "currency": "local",
                "languages": ["English"],
                "coordinates": {"latitude": 0, "longitude": 0},
                "tips": [],
            }

            for line in raw.split("\n"):
                if line.startswith("Country:"):
                    parsed["country"] = line.replace("Country:", "").strip()
                if line.startswith("Capital:"):
                    parsed["capital"] = line.replace("Capital:", "").strip()
                if line.startswith("Population:"):
                    parsed["population"] = line.replace("Population:", "").strip()
                if line.startswith("Timezones:"):
                    parsed["timezone"] = line.replace("Timezones:", "").strip()
                if line.startswith("Currency:"):
                    parsed["currency"] = line.replace("Currency:", "").strip()
                if line.startswith("Languages:"):
                    langs = line.replace("Languages:", "").strip()
                    parsed["languages"] = [item.strip() for item in langs.split(",") if item.strip()]
                if line.startswith("Coordinates:"):
                    coords = line.replace("Coordinates:", "").strip()
                    if "Lat" in coords and "Lon" in coords:
                        lat_part = coords.split("Lat")[1].split(",")[0].strip()
                        lon_part = coords.split("Lon")[1].strip()
                        parsed["coordinates"] = {
                            "latitude": float(lat_part),
                            "longitude": float(lon_part),
                        }

            return parsed
        except ImportError:
            # Fallback to sample destination data
            destinations = {
                "Tokyo": {
                    "country": "Japan",
                    "capital": "Tokyo",
                    "population": "37.4 million",
                    "timezone": "JST (UTC+9)",
                    "currency": "JPY",
                    "languages": ["Japanese"],
                    "coordinates": {"latitude": 35.6762, "longitude": 139.6503},
                    "tips": [
                        "Use the extensive train system for transportation",
                        "Cash is still widely used despite modernization",
                        "Respect local customs and remove shoes when required"
                    ]
                },
                "Paris": {
                    "country": "France",
                    "capital": "Paris",
                    "population": "2.2 million",
                    "timezone": "CET (UTC+1)",
                    "currency": "EUR",
                    "languages": ["French", "English"],
                    "coordinates": {"latitude": 48.8566, "longitude": 2.3522},
                    "tips": [
                        "Learn basic French phrases for better interactions",
                        "The Métro is the best way to navigate the city",
                        "Visit museums on free entry evenings"
                    ]
                },
                "Bali": {
                    "country": "Indonesia",
                    "capital": "Denpasar",
                    "population": "4 million",
                    "timezone": "WITA (UTC+8)",
                    "currency": "IDR",
                    "languages": ["Indonesian", "English"],
                    "coordinates": {"latitude": -8.6705, "longitude": 115.2126},
                    "tips": [
                        "Respect local temples and wear appropriate attire",
                        "Motorbike taxis are convenient and affordable",
                        "Try local street food for authentic cuisine"
                    ]
                }
            }
            
            # Case-insensitive lookup
            dest_data = None
            for key, value in destinations.items():
                if key.lower() == name.lower():
                    dest_data = value
                    break
            
            # If not found, return generated data
            if not dest_data:
                dest_data = {
                    "country": name,
                    "capital": name,
                    "population": "Unknown",
                    "timezone": "UTC",
                    "currency": "local",
                    "languages": ["English"],
                    "coordinates": {"latitude": 0, "longitude": 0},
                    "tips": [
                        "Explore local attractions",
                        "Try local cuisine",
                        "Respect local customs"
                    ]
                }
            
            return dest_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/transport")
async def get_transport(request: TransportRequest):
    try:
        from backend.tools.transport_tool import get_transport_options_data
        return get_transport_options_data(
            from_city=request.origin,
            to_city=request.destination,
            date=request.date,
            currency="INR",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transport")
async def get_transport_v2(
    from_city: str = Query(..., alias="from"),
    to_city: str = Query(..., alias="to"),
    date: str = Query(...),
    currency: str = Query("INR"),
):
    try:
        from backend.tools.transport_tool import get_transport_options_data
        return get_transport_options_data(
            from_city=from_city,
            to_city=to_city,
            date=date,
            currency=currency,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/food")
async def get_food_budget(request: FoodRequest):
    try:
        from backend.tools.food_price_tool import estimate_food_prices
        data = estimate_food_prices.run(
            {
                "city": request.city,
                "country": request.country or "",
                "days": request.days,
                "budget_level": request.budget_level,
            }
        )
        return json.loads(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/budget")
async def get_budget(request: BudgetRequest):
    try:
        from backend.tools.budget_tool import calculate_trip_budget
        data = calculate_trip_budget.run(
            {
                "destination": request.destination,
                "origin": request.origin,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "travelers": request.travelers,
                "budget_level": request.budget_level,
            }
        )
        return json.loads(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/budget-breakdown")
async def get_budget_breakdown(request: BudgetBreakdownRequest):
    try:
        destination_country = _normalize_country_label(request.destination)

        hotel_base = {
            "budget": 1500,
            "moderate": 4000,
            "luxury": 12000,
        }
        food_base = {
            "budget": 800,
            "moderate": 2000,
            "luxury": 5000,
        }
        activities_base = {
            "budget": 500,
            "moderate": 1500,
            "luxury": 4000,
        }

        destination_multiplier = {
            "India": 1.0,
            "Thailand": 1.2,
            "Indonesia": 1.1,
            "France": 3.5,
            "Japan": 3.0,
            "UK": 4.0,
            "USA": 3.8,
            "Australia": 3.2,
            "Singapore": 3.5,
            "UAE": 2.5,
            "default": 2.0,
        }

        food_multiplier = {
            "India": 1.0,
            "Thailand": 0.9,
            "Indonesia": 0.9,
            "France": 2.4,
            "Japan": 2.2,
            "UK": 2.8,
            "USA": 2.6,
            "Australia": 2.4,
            "Singapore": 2.3,
            "UAE": 2.0,
            "default": 1.8,
        }

        level = (request.budgetLevel or "moderate").strip().lower()
        level = level if level in {"budget", "moderate", "luxury"} else "moderate"
        nights = max(int(request.duration), 1)
        adults = max(int(request.adults), 1)

        hotel_mult = destination_multiplier.get(destination_country, destination_multiplier["default"])
        food_mult = food_multiplier.get(destination_country, food_multiplier["default"])

        transport_amount = 0.0
        transport_source = "not_applicable"
        transport_confidence = "high"
        transport_detail = "No origin city provided"

        if (request.origin or "").strip():
            from backend.tools.flight_tool import search_flights_structured

            flight_result = search_flights_structured(
                from_city=request.origin,
                to_city=request.destination,
                departure_date=request.departureDate,
                currency=request.budgetCurrency,
                adults=adults,
                max_results=5,
            )

            if flight_result.get("success") and flight_result.get("offers"):
                cheapest = min(flight_result["offers"], key=lambda item: item.get("price", float("inf")))
                transport_amount = float(cheapest.get("price", 0.0)) * adults
                transport_source = "travelpayouts_live"
                transport_confidence = "high"
                stops = int(cheapest.get("stops", 0))
                stop_text = "Direct" if stops == 0 else ("1 stop" if stops == 1 else f"{stops} stops")
                transport_detail = (
                    f"Cheapest flight: {cheapest.get('airline', 'Airline')} {stop_text} - "
                    f"{request.budgetCurrency} {transport_amount:,.0f}"
                )
            else:
                estimated_inr = _estimate_flight_fallback_inr(request.origin, request.destination)
                amount = _convert_amount_safe("INR", request.budgetCurrency, estimated_inr)
                transport_amount = float(amount) * adults
                transport_source = "estimated"
                transport_confidence = "low"
                if flight_result.get("error_type") == "test_mode_limited":
                    transport_detail = "Live pricing unavailable for this route from free provider. Estimated with distance heuristic."
                elif flight_result.get("error_type") == "quota_exceeded":
                    transport_detail = "Free flight API quota exceeded. Estimated with distance heuristic."
                else:
                    transport_detail = "Live flight lookup unavailable. Estimated with distance heuristic."

        hotel_per_night_inr = hotel_base[level] * hotel_mult
        food_per_day_inr = food_base[level] * food_mult
        activity_per_day_inr = activities_base[level]

        accommodation_amount = _convert_amount_safe("INR", request.budgetCurrency, hotel_per_night_inr * nights)
        food_amount = _convert_amount_safe("INR", request.budgetCurrency, food_per_day_inr * nights)
        activities_amount = _convert_amount_safe("INR", request.budgetCurrency, activity_per_day_inr * nights)

        # Multiply non-transport categories by group size.
        accommodation_amount *= adults
        food_amount *= adults
        activities_amount *= adults

        subtotal = transport_amount + accommodation_amount + food_amount + activities_amount
        misc_amount = subtotal * 0.10
        total = subtotal + misc_amount

        overage = max(total - float(request.budgetAmount), 0.0)
        within_budget = overage <= 0

        return {
            "breakdown": {
                "transport": {
                    "amount": round(transport_amount, 2),
                    "currency": request.budgetCurrency,
                    "source": transport_source,
                    "confidence": transport_confidence,
                    "detail": transport_detail,
                },
                "accommodation": {
                    "amount": round(accommodation_amount, 2),
                    "currency": request.budgetCurrency,
                    "source": "estimated",
                    "confidence": "medium",
                    "detail": (
                        f"{level.title()} hotel, {nights} nights x approximately {request.budgetCurrency} "
                        f"{(accommodation_amount / max(nights * adults, 1)):,.0f}/night"
                    ),
                },
                "food": {
                    "amount": round(food_amount, 2),
                    "currency": request.budgetCurrency,
                    "source": "estimated",
                    "confidence": "medium",
                    "detail": (
                        f"Approximately {request.budgetCurrency} {(food_amount / max(nights * adults, 1)):,.0f}/day x {nights} days"
                    ),
                },
                "activities": {
                    "amount": round(activities_amount, 2),
                    "currency": request.budgetCurrency,
                    "source": "estimated",
                    "confidence": "low",
                    "detail": "Estimated for sightseeing and local experiences.",
                },
                "misc": {
                    "amount": round(misc_amount, 2),
                    "currency": request.budgetCurrency,
                    "source": "calculated",
                    "confidence": "high",
                    "detail": "10% buffer on subtotal",
                },
            },
            "total": round(total, 2),
            "currency": request.budgetCurrency,
            "withinBudget": within_budget,
            "overage": round(overage, 2),
            "adults": adults,
            "perPerson": round(total / adults, 2),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/places/suggest")
async def suggest_places(q: str = Query(..., min_length=1), limit: int = Query(8, ge=1, le=10)):
    try:
        geo_url = "https://nominatim.openstreetmap.org/search"
        geo_params = {
            "q": q,
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": limit,
            "dedupe": 1,
        }
        headers = {"User-Agent": "WandrPlanner/1.0"}
        response = requests.get(geo_url, params=geo_params, headers=headers, timeout=15)
        response.raise_for_status()

        suggestions: List[PlaceSuggestion] = []
        for item in response.json():
            address = item.get("address", {}) or {}
            city = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("hamlet")
                or address.get("municipality")
                or item.get("name")
                or item.get("display_name", "").split(",")[0]
            )
            suggestions.append(
                PlaceSuggestion(
                    name=item.get("name") or city,
                    display_name=item.get("display_name", city),
                    city=city,
                    country=address.get("country", ""),
                    type=item.get("type", ""),
                )
            )

        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calendar/export")
async def export_calendar(request: CalendarExportRequest):
    try:
        from backend.tools.calendar_tool import generate_trip_ics
        payload = {
            "destination": request.destination,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "events": [event.dict() for event in request.events],
        }
        data = json.loads(generate_trip_ics.run(payload))
        if "ics_path" not in data:
            raise HTTPException(status_code=400, detail=data.get("error", "Failed to generate ICS"))
        from urllib.parse import quote
        download_path = quote(data["ics_path"], safe="")
        return {"download_url": "/calendar/download?path=" + download_path, "event_count": data["event_count"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/calendar/download")
async def download_calendar(path: str):
    try:
        from fastapi.responses import FileResponse
        from urllib.parse import unquote
        file_path = unquote(path)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="ICS file not found")
        return FileResponse(
            file_path,
            media_type="text/calendar",
            filename="trip.ics",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SERVE ====================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
