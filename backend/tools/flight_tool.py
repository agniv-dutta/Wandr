import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

TP_PRICES_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
TP_AUTOCOMPLETE_URL = "https://autocomplete.travelpayouts.com/places2"

AIRLINE_NAMES = {
    "AI": "Air India",
    "6E": "IndiGo",
    "EK": "Emirates",
    "BA": "British Airways",
    "LH": "Lufthansa",
    "AF": "Air France",
    "SQ": "Singapore Airlines",
    "JL": "Japan Airlines",
    "NH": "ANA",
    "UA": "United Airlines",
    "DL": "Delta",
    "AA": "American Airlines",
    "QF": "Qantas",
    "QR": "Qatar Airways",
    "EY": "Etihad",
    "TK": "Turkish Airlines",
}


def _estimate_price_range_inr(origin_city: str, destination_city: str) -> Tuple[int, int]:
    origin = origin_city.lower()
    destination = destination_city.lower()

    if origin == destination:
        return 2000, 5000

    india_cities = {
        "mumbai", "delhi", "bangalore", "chennai", "kolkata", "hyderabad", "pune", "goa", "ahmedabad"
    }
    if origin in india_cities and destination in india_cities:
        return 4500, 15000

    long_haul_markers = {
        "new york", "london", "paris", "tokyo", "sydney", "los angeles", "toronto", "frankfurt"
    }
    if origin in long_haul_markers or destination in long_haul_markers:
        return 35000, 95000

    return 18000, 60000


def _normalize_date_or_default(date_text: Optional[str]) -> str:
    if date_text:
        return date_text
    return (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")


def _extract_date_and_route(query: str) -> Tuple[str, Optional[str]]:
    text = " ".join((query or "").strip().split())
    if not text:
        return "", None

    match = re.search(r"(\d{4}-\d{2}-\d{2})$", text)
    if match:
        date_text = match.group(1)
        route_text = text[: match.start()].strip()
        return route_text, date_text

    return text, None


def _split_candidates(route_text: str) -> List[Tuple[str, str]]:
    cleaned = " ".join(route_text.strip().split())
    if not cleaned:
        return []

    lower = cleaned.lower()
    if " to " in lower:
        idx = lower.index(" to ")
        return [(cleaned[:idx].strip(), cleaned[idx + 4 :].strip())]

    tokens = cleaned.split()
    if len(tokens) < 2:
        return []

    candidates: List[Tuple[str, str]] = []
    for split_idx in range(1, len(tokens)):
        left = " ".join(tokens[:split_idx]).strip()
        right = " ".join(tokens[split_idx:]).strip()
        if left and right:
            candidates.append((left, right))

    candidates.sort(key=lambda pair: abs(len(pair[0].split()) - len(pair[1].split())))
    return candidates


def _parse_duration_to_minutes(duration_str: str) -> int:
    if not duration_str:
        return 0

    h_match = re.search(r"(\d+)\s*h", duration_str, flags=re.IGNORECASE)
    m_match = re.search(r"(\d+)\s*m", duration_str, flags=re.IGNORECASE)
    hours = int(h_match.group(1)) if h_match else 0
    minutes = int(m_match.group(1)) if m_match else 0

    if hours == 0 and minutes == 0:
        num = re.search(r"(\d+)", duration_str)
        if num:
            return int(num.group(1))

    return hours * 60 + minutes


def _duration_label(minutes: int) -> str:
    if minutes <= 0:
        return "N/A"
    return f"{minutes // 60}h {minutes % 60:02d}m"


def _resolve_iata(city_name: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    def _candidates(value: str) -> List[str]:
        cleaned = " ".join((value or "").strip().split())
        if not cleaned:
            return []
        parts = [cleaned]
        for sep in [",", "/", "-"]:
            if sep in cleaned:
                parts.append(cleaned.split(sep)[0].strip())
        return list(dict.fromkeys([p for p in parts if p]))

    for term in _candidates(city_name):
        try:
            response = requests.get(
                TP_AUTOCOMPLETE_URL,
                params={
                    "term": term,
                    "locale": "en",
                    "types[]": ["city", "airport"],
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                continue

            preferred = next((item for item in data if item.get("type") == "city"), data[0])
            code = preferred.get("code") or preferred.get("iata") or preferred.get("airport_iata")
            name = preferred.get("name") or term

            if code and len(code) == 3:
                return code.upper(), name, None
        except requests.Timeout:
            return None, city_name, "lookup_timeout"
        except Exception:
            continue

    return None, city_name, "invalid_iata"


def _fetch_travelpayouts_prices(origin_iata: str, destination_iata: str, departure_date: str, currency: str) -> Dict:
    token = os.getenv("TRAVELPAYOUTS_API_TOKEN")
    if not token:
        return {"ok": False, "error_type": "missing_token", "message": "TRAVELPAYOUTS_API_TOKEN is missing."}

    try:
        response = requests.get(
            TP_PRICES_URL,
            params={
                "origin": origin_iata,
                "destination": destination_iata,
                "departure_at": departure_date,
                "currency": currency,
                "token": token,
                "one_way": "true",
                "sorting": "price",
                "limit": 10,
            },
            timeout=20,
        )

        if response.status_code == 429:
            return {"ok": False, "error_type": "quota_exceeded", "message": "API quota exceeded (429)."}

        if response.status_code >= 400:
            return {
                "ok": False,
                "error_type": "api_error",
                "message": f"Provider API error: HTTP {response.status_code}",
            }

        payload = response.json()
        data = payload.get("data") or []
        if isinstance(data, dict):
            data = list(data.values())

        return {"ok": True, "data": data}
    except requests.Timeout:
        return {"ok": False, "error_type": "timeout", "message": "Provider request timed out."}
    except Exception as exc:
        return {"ok": False, "error_type": "exception", "message": str(exc)}


def _parse_offer(item: Dict, origin_iata: str, destination_iata: str, default_currency: str) -> Dict:
    airline_code = (item.get("airline") or "").upper()
    airline = AIRLINE_NAMES.get(airline_code, airline_code or "Unknown Airline")

    departure_raw = item.get("departure_at") or item.get("depart_at") or ""
    dep_time = "--:--"
    arr_time = "--:--"
    day_offset = 0

    try:
        dep_dt = datetime.fromisoformat(str(departure_raw).replace("Z", "+00:00"))
        dep_time = dep_dt.strftime("%H:%M")

        duration_min = int(item.get("duration_to") or item.get("duration") or 0)
        if duration_min <= 0:
            duration_min = _parse_duration_to_minutes(str(item.get("duration_text") or ""))

        if duration_min > 0:
            arr_dt = dep_dt + timedelta(minutes=duration_min)
            arr_time = arr_dt.strftime("%H:%M")
            day_offset = (arr_dt.date() - dep_dt.date()).days
    except Exception:
        duration_min = int(item.get("duration_to") or item.get("duration") or 0)

    stops = int(item.get("transfers") or item.get("number_of_changes") or 0)
    price = float(item.get("price") or 0)
    currency = item.get("currency") or default_currency

    return {
        "airline": airline,
        "airlineCode": airline_code,
        "departureTime": dep_time,
        "arrivalTime": arr_time,
        "arrivalDayOffset": day_offset,
        "duration": _duration_label(duration_min),
        "durationMinutes": duration_min,
        "stops": stops,
        "price": price,
        "currency": currency,
        "route": f"{origin_iata} -> {destination_iata}",
    }


def search_flights_structured(
    from_city: str,
    to_city: str,
    departure_date: Optional[str] = None,
    currency: str = "INR",
    adults: int = 1,
    max_results: int = 5,
) -> Dict:
    _ = adults
    date_str = _normalize_date_or_default(departure_date)

    origin_iata, origin_name, origin_err = _resolve_iata(from_city)
    if origin_err:
        return {
            "success": False,
            "error_type": "invalid_iata",
            "message": f"Invalid IATA lookup for origin city '{from_city}' (resolved label: {origin_name}).",
            "origin_city": from_city,
            "destination_city": to_city,
            "departure_date": date_str,
        }

    destination_iata, destination_name, destination_err = _resolve_iata(to_city)
    if destination_err:
        return {
            "success": False,
            "error_type": "invalid_iata",
            "message": f"Invalid IATA lookup for destination city '{to_city}' (resolved label: {destination_name}).",
            "origin_city": origin_name or from_city,
            "destination_city": to_city,
            "departure_date": date_str,
        }

    fetched = _fetch_travelpayouts_prices(origin_iata, destination_iata, date_str, currency)
    if not fetched.get("ok"):
        err_type = fetched.get("error_type", "api_error")
        low, high = _estimate_price_range_inr(from_city, to_city)

        if err_type == "quota_exceeded":
            return {
                "success": False,
                "error_type": "quota_exceeded",
                "message": fetched.get("message", "API quota exceeded."),
                "estimated_range": [low, high],
                "currency": "INR",
                "origin_city": origin_name or from_city,
                "destination_city": destination_name or to_city,
                "origin_iata": origin_iata,
                "destination_iata": destination_iata,
                "departure_date": date_str,
            }

        return {
            "success": False,
            "error_type": "test_mode_limited",
            "message": "Live pricing unavailable for this route from the free provider.",
            "estimated_range": [low, high],
            "currency": "INR",
            "origin_city": origin_name or from_city,
            "destination_city": destination_name or to_city,
            "origin_iata": origin_iata,
            "destination_iata": destination_iata,
            "departure_date": date_str,
        }

    offers_raw = fetched.get("data", [])
    if not offers_raw:
        low, high = _estimate_price_range_inr(from_city, to_city)
        return {
            "success": False,
            "error_type": "no_flights",
            "message": "No flights found for this route/date.",
            "estimated_range": [low, high],
            "currency": "INR",
            "origin_city": origin_name or from_city,
            "destination_city": destination_name or to_city,
            "origin_iata": origin_iata,
            "destination_iata": destination_iata,
            "departure_date": date_str,
        }

    offers = [_parse_offer(item, origin_iata, destination_iata, currency) for item in offers_raw]
    offers = [item for item in offers if item.get("price", 0) > 0]
    offers.sort(key=lambda item: item.get("price", float("inf")))
    offers = offers[: max(1, min(3, max_results))]

    if not offers:
        low, high = _estimate_price_range_inr(from_city, to_city)
        return {
            "success": False,
            "error_type": "no_flights",
            "message": "No valid priced flights found.",
            "estimated_range": [low, high],
            "currency": "INR",
            "origin_city": origin_name or from_city,
            "destination_city": destination_name or to_city,
            "origin_iata": origin_iata,
            "destination_iata": destination_iata,
            "departure_date": date_str,
        }

    return {
        "success": True,
        "origin_city": origin_name or from_city,
        "destination_city": destination_name or to_city,
        "origin_iata": origin_iata,
        "destination_iata": destination_iata,
        "departure_date": date_str,
        "currency": currency,
        "offers": offers,
        "provider": "travelpayouts_free",
    }


@tool
def search_flights(query: str) -> str:
    """
    Searches for real flight prices between two cities.
    Use this when the user mentions an origin city OR asks about flight costs or transport options.
    Input format: "FROM_CITY TO_CITY DATE"
    If no date is provided, a date 30 days from today is used.
    """
    route_text, parsed_date = _extract_date_and_route(query)
    candidates = _split_candidates(route_text)

    if not candidates:
        return (
            "Invalid format. Use: 'FROM_CITY TO_CITY YYYY-MM-DD'\n"
            "Examples: 'Mumbai Tokyo 2026-05-15', 'New York to Paris 2026-06-01'"
        )

    picked_from = ""
    picked_to = ""
    result: Dict = {}

    for from_candidate, to_candidate in candidates:
        picked_from = from_candidate
        picked_to = to_candidate
        result = search_flights_structured(
            from_city=from_candidate,
            to_city=to_candidate,
            departure_date=parsed_date,
            currency="INR",
            adults=1,
            max_results=5,
        )
        if result.get("success"):
            break
        if result.get("error_type") in {"quota_exceeded", "test_mode_limited", "no_flights"}:
            break

    if not result:
        return "Unable to parse route. Please provide origin and destination cities."

    if not result.get("success"):
        err_type = result.get("error_type")
        if err_type == "invalid_iata":
            return f"IATA lookup failed. {result.get('message', '')}"

        low, high = result.get("estimated_range", [18000, 60000])
        if err_type == "quota_exceeded":
            return (
                "Free flight API quota exceeded (429).\n"
                f"Estimated range (clearly labelled): approximately INR {low:,} - INR {high:,}."
            )

        return (
            "Live pricing unavailable from free provider for this route/date.\n"
            f"Estimated range (clearly labelled): approximately INR {low:,} - INR {high:,}."
        )

    offers = result.get("offers", [])
    origin_city = result.get("origin_city", picked_from)
    destination_city = result.get("destination_city", picked_to)
    origin_iata = result.get("origin_iata", "")
    destination_iata = result.get("destination_iata", "")
    currency = offers[0].get("currency", "INR") if offers else "INR"

    lines = [
        f"Flight Options from {origin_city} ({origin_iata}) to {destination_city} ({destination_iata}):",
        "-" * 55,
    ]

    for idx, offer in enumerate(offers[:3], start=1):
        stop_label = "Direct" if offer["stops"] == 0 else ("1 stop" if offer["stops"] == 1 else f"{offer['stops']} stops")
        arr_suffix = f" (+{offer['arrivalDayOffset']})" if offer["arrivalDayOffset"] > 0 else ""

        lines.append(
            f"{idx}. {offer['airline']} | Dep: {offer['departureTime']} | Arr: {offer['arrivalTime']}{arr_suffix} | "
            f"Duration: {offer['duration']} | {stop_label} | {offer['currency']} {offer['price']:,.0f}"
        )

    lines.append("-" * 55)
    lines.append(f"Prices in {currency}. Source: Travelpayouts free API.")
    return "\n".join(lines)
