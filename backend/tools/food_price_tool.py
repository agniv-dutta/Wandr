import json
import re
import hashlib
import html
from urllib.parse import urlparse, parse_qs, unquote
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

MEAL_STYLE_VARIANTS: Dict[str, List[str]] = {
    "lunch": [
        "at a local family-run spot",
        "from an old-town market kitchen",
        "with a scenic city-view setting",
        "in a traditional neighborhood tavern",
        "as a street-food style plate",
        "as a chef's tasting portion",
    ],
    "dinner": [
        "with sunset waterfront seating",
        "in a heritage dining room",
        "paired with regional house specialties",
        "in a lively evening food district",
        "as a slow-cooked signature meal",
        "with a modern fusion presentation",
    ],
}


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
    """Normalize free-form location text to a supported country key."""
    raw_candidates = [country or "", city or ""]

    # Try exact and tokenized matches first.
    for raw in raw_candidates:
        lowered = raw.strip().lower()
        if not lowered:
            continue
        if lowered in BUDGET_BASE_PRICES:
            return lowered

        tokens = [t.strip() for t in re.split(r"[,/()\-]", lowered) if t.strip()]
        for token in tokens:
            if token in BUDGET_BASE_PRICES:
                return token

    # Fallback to substring matching (e.g., "zagreb, croatia").
    combined = " ".join(raw_candidates).lower()
    for key in BUDGET_BASE_PRICES.keys():
        if key in combined:
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


def _clean_context_hint(context: str) -> str:
    tokens = re.findall(r"[a-zA-Z]{3,}", (context or "").lower())
    stop = {
        "morning", "afternoon", "evening", "visit", "explore", "day",
        "local", "travel", "trip", "activity", "activities", "around",
        "near", "with", "from", "your", "this", "that",
    }
    filtered = [t for t in tokens if t not in stop]
    return " ".join(filtered[:5])


def _segment_day_context(context: str) -> Dict[str, str]:
    """Extract morning/afternoon/evening text chunks from itinerary day context."""
    raw = (context or "").strip()
    if not raw:
        return {"morning": "", "afternoon": "", "evening": "", "full": ""}

    # Normalize markdown emphasis and delimiters from itinerary text.
    normalized = re.sub(r"\*+", "", raw)

    morning = ""
    afternoon = ""
    evening = ""

    m = re.search(r"morning\s*:\s*(.*?)(?=afternoon\s*:|evening\s*:|$)", normalized, flags=re.IGNORECASE)
    a = re.search(r"afternoon\s*:\s*(.*?)(?=evening\s*:|$)", normalized, flags=re.IGNORECASE)
    e = re.search(r"evening\s*:\s*(.*?)(?=$)", normalized, flags=re.IGNORECASE)

    if m:
        morning = m.group(1).strip(" ;,-")
    if a:
        afternoon = a.group(1).strip(" ;,-")
    if e:
        evening = e.group(1).strip(" ;,-")

    if not (morning or afternoon or evening):
        parts = [p.strip() for p in re.split(r";|\|", normalized) if p.strip()]
        if parts:
            morning = parts[0] if len(parts) > 0 else ""
            afternoon = parts[1] if len(parts) > 1 else morning
            evening = parts[2] if len(parts) > 2 else afternoon

    return {
        "morning": morning,
        "afternoon": afternoon,
        "evening": evening,
        "full": normalized,
    }


def _extract_web_results(search_html: str) -> List[Dict[str, str]]:
    if not search_html:
        return []

    link_pattern = re.compile(
        r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    snippet_pattern = re.compile(
        r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>|<div[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</div>',
        flags=re.IGNORECASE | re.DOTALL,
    )

    links = link_pattern.findall(search_html)
    snippets_raw = snippet_pattern.findall(search_html)
    snippets = []
    for a, b in snippets_raw:
        text = a or b or ""
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", html.unescape(text)).strip()
        if text:
            snippets.append(text)

    results: List[Dict[str, str]] = []
    for i, (href, title_html) in enumerate(links[:10]):
        title = re.sub(r"<[^>]+>", " ", title_html)
        title = re.sub(r"\s+", " ", html.unescape(title)).strip()

        resolved_url = href
        parsed = urlparse(href)
        if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
            params = parse_qs(parsed.query)
            uddg = params.get("uddg", [""])[0]
            if uddg:
                resolved_url = unquote(uddg)

        if resolved_url.startswith("//"):
            resolved_url = f"https:{resolved_url}"

        snippet = snippets[i] if i < len(snippets) else ""
        if title:
            results.append({"title": title, "snippet": snippet, "url": resolved_url})

    return results


def _pick_varied_meal_suggestion(
    country_key: str,
    meal_type: str,
    day: int,
    theme: str,
    context: str,
    recent: List[str],
) -> str:
    """Select meal suggestions with deterministic day-wise variation and no immediate repeats."""
    pool = REGIONAL_SPECIALTIES.get(country_key, {}).get(meal_type, [])
    if not pool:
        pool = [
            _get_meal_suggestions(country_key, meal_type, day, 0),
            _get_meal_suggestions(country_key, meal_type, day + 1, 1),
            _get_meal_suggestions(country_key, meal_type, day + 2, 2),
        ]

    seed = f"{country_key}|{meal_type}|{day}|{theme}|{context or ''}".lower()
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    if meal_type in MEAL_STYLE_VARIANTS:
        styles = MEAL_STYLE_VARIANTS[meal_type]
        combos = [f"{dish} ({style})" for dish in pool for style in styles]
        blocked = set(recent)
        candidates = [item for item in combos if item not in blocked] or combos
    else:
        blocked = set(recent[-2:])
        candidates = [item for item in pool if item not in blocked] or pool

    index = int(digest[:8], 16) % len(candidates)
    suggestion = candidates[index]

    # Last safety check to prevent immediate repetition when there are alternatives.
    if recent and suggestion == recent[-1] and len(candidates) > 1:
        suggestion = candidates[(index + 1) % len(candidates)]

    return suggestion


def _search_meal_place(
    city: str,
    country: str,
    meal_type: str,
    theme: str,
    context: str,
    phase_hint: str,
    fallback_suggestion: str,
    fallback_amount: float,
    currency: str,
    search_cache: Dict[str, List[Dict[str, str]]],
    used_signatures: set,
) -> Dict[str, str]:
    primary_hint = _clean_context_hint(phase_hint)
    secondary_hint = _clean_context_hint(context)
    hint = primary_hint or secondary_hint
    query = f"best {meal_type} restaurant near {hint} {city} {country} {theme} price" if hint else f"best {meal_type} restaurant in {city} {country} {theme} price"
    query = re.sub(r"\s+", " ", query).strip()

    if query not in search_cache:
        search_cache[query] = _extract_web_results(search_web(query))

    candidates = search_cache.get(query, [])
    if not candidates:
        return {
            "suggestion": f"{fallback_suggestion} (~{currency} {round(fallback_amount)})",
            "url": f"https://www.google.com/maps/search/{city}+{theme}+restaurants",
        }

    for cand in candidates:
        raw_title = cand.get("title", "")
        snippet = cand.get("snippet", "")
        url = cand.get("url", "")

        place = re.split(r"\s[\-|\|]\s", raw_title)[0].strip()
        place = re.sub(r"\s+", " ", place)
        if not place or len(place) < 3:
            continue

        signature = f"{meal_type}:{place.lower()}"
        if signature in used_signatures:
            continue

        min_p, max_p, found_currency = extract_price_range(f"{raw_title} {snippet}")
        if min_p is not None and max_p is not None:
            est = round((min_p + max_p) / 2)
        elif min_p is not None:
            est = round(min_p)
        else:
            est = round(fallback_amount)

        shown_currency = found_currency or currency
        used_signatures.add(signature)
        return {
            "suggestion": f"{place} (~{shown_currency} {est})",
            "url": url or f"https://www.google.com/maps/search/{city}+{place}",
        }

    return {
        "suggestion": f"{fallback_suggestion} (~{currency} {round(fallback_amount)})",
        "url": f"https://www.google.com/maps/search/{city}+{theme}+restaurants",
    }


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
    breakfast_history: List[str] = []
    lunch_history: List[str] = []
    dinner_history: List[str] = []
    search_cache: Dict[str, List[Dict[str, str]]] = {}
    used_places: set = set()
    max_web_searches = min(total_days, 4)
    searches_done = 0

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

        breakfast_suggestion = _pick_varied_meal_suggestion(
            country_key,
            "breakfast",
            day,
            theme,
            context,
            breakfast_history,
        )
        lunch_suggestion = _pick_varied_meal_suggestion(
            country_key,
            "lunch",
            day,
            theme,
            context,
            lunch_history,
        )
        dinner_suggestion = _pick_varied_meal_suggestion(
            country_key,
            "dinner",
            day,
            theme,
            context,
            dinner_history,
        )

        lunch_url = f"https://www.google.com/maps/search/{city}+lunch"
        dinner_url = f"https://www.google.com/maps/search/{city}+dinner"

        if searches_done < max_web_searches:
            segments = _segment_day_context(context)
            lunch_pick = _search_meal_place(
                city,
                country,
                "lunch",
                theme,
                context,
                segments.get("afternoon") or segments.get("full") or context,
                lunch_suggestion,
                lunch,
                currency,
                search_cache,
                used_places,
            )
            lunch_suggestion = lunch_pick["suggestion"]
            lunch_url = lunch_pick["url"]
            searches_done += 1

        if searches_done < max_web_searches:
            segments = _segment_day_context(context)
            dinner_pick = _search_meal_place(
                city,
                country,
                "dinner",
                theme,
                context,
                segments.get("evening") or segments.get("full") or context,
                dinner_suggestion,
                dinner,
                currency,
                search_cache,
                used_places,
            )
            dinner_suggestion = dinner_pick["suggestion"]
            dinner_url = dinner_pick["url"]
            searches_done += 1

        breakfast_history.append(breakfast_suggestion)
        lunch_history.append(lunch_suggestion)
        dinner_history.append(dinner_suggestion)

        daily_items.append(
            {
                "day": day,
                "theme": theme,
                "context": context,
                "breakfast": {
                    "amount": breakfast,
                    "suggestion": breakfast_suggestion,
                },
                "lunch": {
                    "amount": lunch,
                    "suggestion": lunch_suggestion,
                },
                "dinner": {
                    "amount": dinner,
                    "suggestion": dinner_suggestion,
                },
                "daily_total": subtotal,
                "lunch_source": lunch_url,
                "dinner_source": dinner_url,
                "nearby_source": lunch_url or dinner_url or f"https://www.google.com/maps/search/{city}+{theme}+restaurants",
            }
        )
        total_food += subtotal

    return {
        "city": city,
        "currency": currency,
        "days": daily_items,
        "daily_average": round(total_food / total_days, 2),
        "total_food_cost": round(total_food, 2),
        "notes": f"Lunch/dinner recommendations include live nearby places when available; estimated meal costs are shown in {currency} or detected listing currency.",
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
