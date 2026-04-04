import json
from typing import Dict, List, Optional

from langchain.tools import tool

from .search_utils import search_web, extract_price_range, extract_first_url


REGIONAL_SPECIALTIES: Dict[str, Dict[str, List[str]]] = {
    "croatia": {
        "breakfast": ["Fresh burek with coffee", "Local pastries", "Rakija and cheese board"],
        "lunch": ["Black risotto (Crni rižoto)", "Grilled Adriatic fish", "Pašticada stew"],
        "dinner": ["Peka (baked meat/fish)", "Octopus salad", "Dalmatian seafood platter"],
    },
    "japan": {
        "breakfast": ["Tamagoyaki (egg omelette)", "Onigiri (rice balls)", "Miso soup with nori"],
        "lunch": ["Ramen with tonkotsu broth", "Tempura set", "Okonomiyaki (savory pancake)"],
        "dinner": ["Yakitori skewers", "Katsu curry meal", "Sushi omakase"],
    },
    "thailand": {
        "breakfast": ["Khao tom (rice soup)", "Mango sticky rice", "Thai toast with condensed milk"],
        "lunch": ["Pad Thai (stir-fried noodles)", "Som Tam (green papaya salad)", "Khao Pad"],
        "dinner": ["Massaman curry", "Khao Soi (Northern curry noodles)", "Tom Yum soup"],
    },
    "france": {
        "breakfast": ["Croissant au chocolat", "Café au lait with pain au raisin", "Omelette"],
        "lunch": ["Nicoise salad", "Croque monsieur sandwich", "Duck confit"],
        "dinner": ["Steak frites", "Onion soup (French)", "Ratatouille with crusty bread"],
    },
    "italy": {
        "breakfast": ["Cornetto with cappuccino", "Panettone", "Fritelle (donuts)"],
        "lunch": ["Risotto Milanese", "Pasta alla carbonara", "Ossobuco"],
        "dinner": ["Neapolitan pizza", "Ravioli with sauce", "Tiramisu for dessert"],
    },
    "india": {
        "breakfast": ["Masala dosa", "Idli with sambar", "Paratha with butter chicken"],
        "lunch": ["Chana masala with naan", "Biryani with raita", "Samosas and chaat"],
        "dinner": ["Thali with curries", "Tandoori chicken", "Paneer makhani with rice"],
    },
    "usa": {
        "breakfast": ["Bagel sandwich with cream cheese", "Pancakes with maple syrup", "Eggs Benedict"],
        "lunch": ["Gourmet burger", "Tacos al pastor", "BBQ brisket sandwich"],
        "dinner": ["Steak and ribs", "Lobster tail", "Cheesecake dessert"],
    },
    "uk": {
        "breakfast": ["Full English breakfast", "Toast with Marmite", "Beans on toast"],
        "lunch": ["Fish and chips", "Cornish pastry", "Bangers and mash"],
        "dinner": ["Beef Wellington", "Shepherd's pie", "Sticky toffee pudding"],
    },
    "mexico": {
        "breakfast": ["Chilaquiles with eggs", "Tamale", "Quesadilla"],
        "lunch": ["Carne asada tacos", "Elote (street corn)", "Mole negro"],
        "dinner": ["Chiles rellenos", "Cochinita pibil", "Churros con chocolate"],
    },
    "spain": {
        "breakfast": ["Churro with hot chocolate", "Pan con tomate", "Jamón Ibérico"],
        "lunch": ["Paella Valenciana", "Gazpacho", "Raciones (Spanish tapas portions)"],
        "dinner": ["Tapas sampler", "Gambas al ajillo", "Pulpo a la gallega"],
    },
}

# Budget-aware base pricing per destination (in local currency)
BUDGET_BASE_PRICES: Dict[str, Dict[str, Dict[str, float]]] = {
    "croatia": {
        "budget": {"breakfast": 30, "lunch": 50, "dinner": 80},
        "moderate": {"breakfast": 60, "lunch": 100, "dinner": 150},
        "luxury": {"breakfast": 150, "lunch": 250, "dinner": 400},
        "currency": "HRK",
    },
    "japan": {
        "budget": {"breakfast": 800, "lunch": 1200, "dinner": 1800},
        "moderate": {"breakfast": 1500, "lunch": 2500, "dinner": 3500},
        "luxury": {"breakfast": 4000, "lunch": 6000, "dinner": 10000},
        "currency": "JPY",
    },
    "thailand": {
        "budget": {"breakfast": 50, "lunch": 100, "dinner": 150},
        "moderate": {"breakfast": 150, "lunch": 250, "dinner": 400},
        "luxury": {"breakfast": 500, "lunch": 800, "dinner": 1500},
        "currency": "THB",
    },
    "france": {
        "budget": {"breakfast": 8, "lunch": 15, "dinner": 25},
        "moderate": {"breakfast": 15, "lunch": 30, "dinner": 50},
        "luxury": {"breakfast": 50, "lunch": 100, "dinner": 200},
        "currency": "EUR",
    },
    "italy": {
        "budget": {"breakfast": 7, "lunch": 12, "dinner": 20},
        "moderate": {"breakfast": 12, "lunch": 25, "dinner": 40},
        "luxury": {"breakfast": 40, "lunch": 80, "dinner": 150},
        "currency": "EUR",
    },
    "india": {
        "budget": {"breakfast": 50, "lunch": 100, "dinner": 150},
        "moderate": {"breakfast": 150, "lunch": 300, "dinner": 450},
        "luxury": {"breakfast": 500, "lunch": 1000, "dinner": 2000},
        "currency": "INR",
    },
    "usa": {
        "budget": {"breakfast": 8, "lunch": 12, "dinner": 20},
        "moderate": {"breakfast": 18, "lunch": 30, "dinner": 50},
        "luxury": {"breakfast": 50, "lunch": 100, "dinner": 250},
        "currency": "USD",
    },
    "uk": {
        "budget": {"breakfast": 6, "lunch": 10, "dinner": 18},
        "moderate": {"breakfast": 12, "lunch": 25, "dinner": 40},
        "luxury": {"breakfast": 40, "lunch": 80, "dinner": 150},
        "currency": "GBP",
    },
    "mexico": {
        "budget": {"breakfast": 80, "lunch": 150, "dinner": 220},
        "moderate": {"breakfast": 200, "lunch": 350, "dinner": 500},
        "luxury": {"breakfast": 600, "lunch": 1000, "dinner": 1800},
        "currency": "MXN",
    },
    "spain": {
        "budget": {"breakfast": 5, "lunch": 10, "dinner": 15},
        "moderate": {"breakfast": 12, "lunch": 22, "dinner": 35},
        "luxury": {"breakfast": 35, "lunch": 70, "dinner": 130},
        "currency": "EUR",
    },
}


THEME_MULTIPLIER = {
    "beach": 1.08,
    "nightlife": 1.15,
    "adventure": 1.05,
    "shopping": 1.10,
    "cultural": 0.98,
    "balanced": 1.0,
}


DAY_VARIATION = [0.92, 1.0, 1.08, 0.96, 1.12, 0.95, 1.05]


def _infer_theme(day_context: str) -> str:
    text = (day_context or "").lower()
    if any(k in text for k in ["beach", "island", "coast", "seaside"]):
        return "beach"
    if any(k in text for k in ["bar", "club", "night", "pub", "cocktail"]):
        return "nightlife"
    if any(k in text for k in ["hike", "trek", "climb", "trail", "adventure"]):
        return "adventure"
    if any(k in text for k in ["mall", "market", "shopping", "boutique"]):
        return "shopping"
    if any(k in text for k in ["museum", "heritage", "old town", "cathedral", "temple"]):
        return "cultural"
    return "balanced"


def _get_country_code(city: str, country: str) -> str:
    """Normalize country name to lowercase key"""
    candidates = [
        (country or "").strip().lower(),
        (city or "").strip().lower(),
    ]
    for key in candidates:
        if key in BUDGET_BASE_PRICES:
            return key
    # Default to USA if not found
    return "usa"


def _get_meal_suggestions(country_key: str, meal_type: str, day: int, rotation: int = 0) -> str:
    """Get specific meal suggestion for the day"""
    pool = REGIONAL_SPECIALTIES.get(country_key, {}).get(meal_type, [])
    
    if not pool:
        # Fallback generic suggestions per meal type
        fallbacks = {
            "breakfast": [
                "Local breakfast specialty",
                "Traditional morning dish",
                "Street breakfast",
                "Café breakfast combo",
            ],
            "lunch": [
                "Local lunch specialty",
                "Regional signature dish",
                "Street food favorite",
                "Market lunch special",
            ],
            "dinner": [
                "Local dinner specialty",
                "Regional evening favorite",
                "Restaurant signature",
                "Local street dinner",
            ],
        }
        pool = fallbacks.get(meal_type, ["Local specialty"])
    
    idx = (day + rotation) % len(pool)
    return pool[idx]


def build_daily_food_plan(city: str, country: str, days: int, budget_level: str, day_contexts: Optional[List[str]] = None) -> Dict:
    budget_level = (budget_level or "moderate").lower()
    country_key = _get_country_code(city, country)
    budget_data = BUDGET_BASE_PRICES.get(country_key, BUDGET_BASE_PRICES["usa"])
    
    day_contexts = day_contexts or []
    total_days = max(int(days), 1)
    
    base_prices = budget_data.get(budget_level, budget_data.get("moderate"))
    currency = budget_data.get("currency", "USD")

    daily_items: List[Dict] = []
    total_food = 0.0

    for day in range(1, total_days + 1):
        context = day_contexts[day - 1] if day - 1 < len(day_contexts) else ""
        theme = _infer_theme(context)
        variation = DAY_VARIATION[(day - 1) % len(DAY_VARIATION)]
        theme_factor = THEME_MULTIPLIER.get(theme, 1.0)
        factor = variation * theme_factor

        breakfast = round(base_prices["breakfast"] * factor, 2)
        lunch = round(base_prices["lunch"] * factor, 2)
        dinner = round(base_prices["dinner"] * factor, 2)
        subtotal = round(breakfast + lunch + dinner, 2)

        daily_items.append(
            {
                "day": day,
                "theme": theme,
                "context": context,
                "breakfast": {
                    "amount": breakfast,
                    "suggestion": _get_meal_suggestions(country_key, "breakfast", day, 0),
                },
                "lunch": {
                    "amount": lunch,
                    "suggestion": _get_meal_suggestions(country_key, "lunch", day, 1),
                },
                "dinner": {
                    "amount": dinner,
                    "suggestion": _get_meal_suggestions(country_key, "dinner", day, 2),
                },
                "daily_total": subtotal,
                "nearby_source": f"https://www.google.com/maps/search/{city}+{theme}+restaurants",
            }
        )
        total_food += subtotal

    return {
        "city": city,
        "currency": currency,
        "days": daily_items,
        "daily_average": round(total_food / total_days, 2),
        "total_food_cost": round(total_food, 2),
        "notes": f"Daily food costs vary by itinerary context, neighborhood, and meal style. Prices in {currency}.",
        "sources": [],
    }


def _quick_food_web_suggestion(city: str, theme: str) -> Optional[str]:
    query = f"best local {theme} food in {city}"
    text = search_web(query)
    url = extract_first_url(text)
    return url


def _search_for_budget(city: str, country: str, budget_level: str) -> Dict:
    country_key = _get_country_code(city, country)
    budget_data = BUDGET_BASE_PRICES.get(country_key, BUDGET_BASE_PRICES["usa"])
    base_prices = budget_data.get(budget_level, budget_data.get("moderate"))
    currency = budget_data.get("currency", "USD")

    return {
        "breakfast_avg": base_prices["breakfast"],
        "lunch_avg": base_prices["lunch"],
        "dinner_avg": base_prices["dinner"],
        "currency": currency,
        "source": "regional_database",
        "url": "",
    }


@tool
def estimate_food_prices(city: str, country: str, days: int, budget_level: str) -> str:
    """
    Estimate per-day food costs for a city.
    Input schema: { city, country, days, budget_level }
    """
    try:
        budget_level = (budget_level or "moderate").lower()
        base = _search_for_budget(city, country, budget_level)
        daily = base["breakfast_avg"] + base["lunch_avg"] + base["dinner_avg"]
        total = daily * max(int(days), 1)

        result = {
            "breakfast_avg": base["breakfast_avg"],
            "lunch_avg": base["lunch_avg"],
            "dinner_avg": base["dinner_avg"],
            "daily_food_budget": round(daily, 2),
            "total_food_cost": round(total, 2),
            "currency": base["currency"],
            "notes": "Prices vary by neighborhood and season.",
            "sources": [base["url"]] if base["url"] else [],
        }

        return json.dumps(result)

    except Exception as exc:
        return json.dumps({"error": str(exc)})
