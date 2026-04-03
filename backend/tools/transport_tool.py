import json
import math
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from langchain.tools import tool

from .flight_tool import search_flights_structured

INDIAN_ROUTE_DATA: Dict[str, Dict] = {
    "mumbai-pune": {
        "train": {"time": "3h", "price_range": "INR 150-800", "frequency": "Hourly"},
        "bus": {"time": "3.5h", "price_range": "INR 200-600", "frequency": "Every 30 min"},
        "flight": {"time": "1h", "price_range": "INR 2500-6000", "frequency": "4 flights/day"},
    },
    "delhi-agra": {
        "train": {"time": "2h", "price_range": "INR 120-950", "frequency": "Every 1-2 hours"},
        "bus": {"time": "4h", "price_range": "INR 250-700", "frequency": "Hourly"},
        "flight": {"time": "N/A", "price_range": "INR 0-0", "frequency": "Limited"},
    },
    "bangalore-chennai": {
        "train": {"time": "5h", "price_range": "INR 180-950", "frequency": "Every 2 hours"},
        "bus": {"time": "6h", "price_range": "INR 350-1200", "frequency": "Every 45 min"},
        "flight": {"time": "1h", "price_range": "INR 2200-6500", "frequency": "8 flights/day"},
    },
    "delhi-mumbai": {
        "train": {"time": "15h", "price_range": "INR 600-3500", "frequency": "Daily"},
        "bus": {"time": "24h", "price_range": "INR 1800-3500", "frequency": "Daily"},
        "flight": {"time": "2h 10m", "price_range": "INR 4200-12000", "frequency": "20+ flights/day"},
    },
    "mumbai-goa": {
        "train": {"time": "8h", "price_range": "INR 350-1800", "frequency": "Daily"},
        "bus": {"time": "11h", "price_range": "INR 900-2200", "frequency": "Every 2 hours"},
        "flight": {"time": "1h 15m", "price_range": "INR 2800-9000", "frequency": "10 flights/day"},
    },
    "kolkata-delhi": {
        "train": {"time": "17h", "price_range": "INR 700-3800", "frequency": "Daily"},
        "bus": {"time": "30h", "price_range": "INR 2200-4800", "frequency": "Daily"},
        "flight": {"time": "2h 20m", "price_range": "INR 4500-13000", "frequency": "12 flights/day"},
    },
    "hyderabad-bangalore": {
        "train": {"time": "10h", "price_range": "INR 300-1600", "frequency": "Daily"},
        "bus": {"time": "9h", "price_range": "INR 700-1900", "frequency": "Hourly"},
        "flight": {"time": "1h 10m", "price_range": "INR 2600-8500", "frequency": "9 flights/day"},
    },
    "chennai-hyderabad": {
        "train": {"time": "12h", "price_range": "INR 350-1750", "frequency": "Daily"},
        "bus": {"time": "11h", "price_range": "INR 850-2200", "frequency": "Every 90 min"},
        "flight": {"time": "1h 20m", "price_range": "INR 3000-9000", "frequency": "8 flights/day"},
    },
    "delhi-jaipur": {
        "train": {"time": "4.5h", "price_range": "INR 200-1200", "frequency": "Every 2 hours"},
        "bus": {"time": "6h", "price_range": "INR 300-1100", "frequency": "Every 30 min"},
        "flight": {"time": "1h", "price_range": "INR 2800-8000", "frequency": "3 flights/day"},
    },
    "delhi-varanasi": {
        "train": {"time": "11h", "price_range": "INR 350-2200", "frequency": "Daily"},
        "bus": {"time": "14h", "price_range": "INR 900-2300", "frequency": "Daily"},
        "flight": {"time": "1h 30m", "price_range": "INR 3200-9500", "frequency": "7 flights/day"},
    },
    "mumbai-ahmedabad": {
        "train": {"time": "6h", "price_range": "INR 250-1400", "frequency": "Every 2 hours"},
        "bus": {"time": "8h", "price_range": "INR 500-1700", "frequency": "Hourly"},
        "flight": {"time": "1h 15m", "price_range": "INR 2500-7800", "frequency": "11 flights/day"},
    },
    "bangalore-goa": {
        "train": {"time": "13h", "price_range": "INR 300-1600", "frequency": "Daily"},
        "bus": {"time": "11h", "price_range": "INR 850-2200", "frequency": "Daily"},
        "flight": {"time": "1h 20m", "price_range": "INR 3200-9800", "frequency": "5 flights/day"},
    },
    "delhi-amritsar": {
        "train": {"time": "6h", "price_range": "INR 220-1300", "frequency": "Every 2 hours"},
        "bus": {"time": "8h", "price_range": "INR 500-1600", "frequency": "Hourly"},
        "flight": {"time": "1h 15m", "price_range": "INR 2600-8400", "frequency": "6 flights/day"},
    },
    "pune-hyderabad": {
        "train": {"time": "10h", "price_range": "INR 300-1700", "frequency": "Daily"},
        "bus": {"time": "11h", "price_range": "INR 700-2200", "frequency": "Daily"},
        "flight": {"time": "1h 20m", "price_range": "INR 3000-9000", "frequency": "6 flights/day"},
    },
    "kolkata-bhubaneswar": {
        "train": {"time": "6h", "price_range": "INR 250-1200", "frequency": "Every 2 hours"},
        "bus": {"time": "7h", "price_range": "INR 450-1200", "frequency": "Hourly"},
        "flight": {"time": "1h", "price_range": "INR 2300-7000", "frequency": "4 flights/day"},
    },
    "chennai-kochi": {
        "train": {"time": "12h", "price_range": "INR 320-1700", "frequency": "Daily"},
        "bus": {"time": "12h", "price_range": "INR 800-2000", "frequency": "Every 2 hours"},
        "flight": {"time": "1h 20m", "price_range": "INR 2800-8600", "frequency": "5 flights/day"},
    },
}

INDIAN_CITY_COORDS = {
    "mumbai": (19.0760, 72.8777),
    "pune": (18.5204, 73.8567),
    "delhi": (28.6139, 77.2090),
    "agra": (27.1767, 78.0081),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "jaipur": (26.9124, 75.7873),
    "varanasi": (25.3176, 82.9739),
    "ahmedabad": (23.0225, 72.5714),
    "goa": (15.2993, 74.1240),
    "amritsar": (31.6340, 74.8723),
    "bhubaneswar": (20.2961, 85.8245),
    "kochi": (9.9312, 76.2673),
}



def _route_key(from_city: str, to_city: str) -> str:
    a = from_city.strip().lower()
    b = to_city.strip().lower()
    return "-".join(sorted([a, b]))


def _parse_price_range_to_min(price_range: str) -> Optional[float]:
    match = re.search(r"(\d+(?:,\d+)?)\s*[-–]\s*(\d+(?:,\d+)?)", price_range)
    if not match:
        return None
    low = float(match.group(1).replace(",", ""))
    return low


def _parse_time_to_hours(time_text: str) -> Optional[float]:
    if not time_text or time_text == "N/A":
        return None

    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)h(?:\s*(\d+)m)?\s*", time_text)
    if match:
        hours = float(match.group(1))
        minutes = float(match.group(2) or 0)
        return hours + minutes / 60

    return None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def _estimate_indian_route(from_city: str, to_city: str) -> Dict[str, Dict[str, str]]:
    a = INDIAN_CITY_COORDS.get(from_city.lower())
    b = INDIAN_CITY_COORDS.get(to_city.lower())

    distance_km = 900.0
    if a and b:
        distance_km = max(_haversine_km(a[0], a[1], b[0], b[1]), 120.0)

    train_hours = max(distance_km / 55, 2.0)
    bus_hours = max(distance_km / 45, 2.5)
    flight_hours = max(distance_km / 700 + 0.8, 1.0)

    train_low = int(distance_km * 0.7)
    train_high = int(distance_km * 1.8)
    bus_low = int(distance_km * 0.8)
    bus_high = int(distance_km * 1.7)
    flight_low = int(distance_km * 5.5)
    flight_high = int(distance_km * 12.5)

    return {
        "train": {
            "time": f"{train_hours:.1f}h",
            "price_range": f"INR {train_low:,}-{train_high:,}",
            "frequency": "Estimated: multiple services/day",
            "source": "estimated",
        },
        "bus": {
            "time": f"{bus_hours:.1f}h",
            "price_range": f"INR {bus_low:,}-{bus_high:,}",
            "frequency": "Estimated: frequent services",
            "source": "estimated",
        },
        "flight": {
            "time": f"{flight_hours:.1f}h",
            "price_range": f"INR {flight_low:,}-{flight_high:,}",
            "frequency": "Estimated",
            "source": "estimated",
        },
    }


def _is_indian_city(city: str) -> bool:
    return city.strip().lower() in INDIAN_CITY_COORDS


def _is_indian_domestic_route(from_city: str, to_city: str) -> bool:
    return _is_indian_city(from_city) and _is_indian_city(to_city)


def _default_date() -> str:
    return (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")


def _build_ground_mode(mode_name: str, raw: Dict) -> Dict:
    min_price = _parse_price_range_to_min(raw.get("price_range", ""))
    duration_hours = _parse_time_to_hours(raw.get("time", ""))

    return {
        "mode": mode_name,
        "journeyTime": raw.get("time", "N/A"),
        "priceRange": raw.get("price_range", "N/A"),
        "frequency": raw.get("frequency", "N/A"),
        "source": raw.get("source", "live"),
        "minPrice": min_price,
        "durationHours": duration_hours,
    }


def get_transport_options_data(from_city: str, to_city: str, date: Optional[str] = None, currency: str = "INR") -> Dict:
    travel_date = date or _default_date()

    flights_data = search_flights_structured(
        from_city=from_city,
        to_city=to_city,
        departure_date=travel_date,
        currency=currency,
        adults=1,
        max_results=5,
    )

    flight_offers = flights_data.get("offers", []) if flights_data.get("success") else []

    indian_route = _is_indian_domestic_route(from_city, to_city)
    route_key = _route_key(from_city, to_city)

    if indian_route:
        route_raw = INDIAN_ROUTE_DATA.get(route_key) or _estimate_indian_route(from_city, to_city)
        trains = {
            "applicable": True,
            "options": [_build_ground_mode("train", route_raw["train"])],
        }
        buses = {
            "applicable": True,
            "options": [_build_ground_mode("bus", route_raw["bus"])],
        }
    else:
        trains = {
            "applicable": False,
            "options": [],
            "message": "Train travel not applicable for international routes.",
        }
        buses = {
            "applicable": False,
            "options": [],
            "message": "Bus travel not applicable for international routes.",
        }

    modes_for_value: List[Tuple[str, float]] = []

    if flight_offers:
        cheapest_flight = min(flight_offers, key=lambda item: item.get("price", float("inf")))
        duration_hours = max((cheapest_flight.get("durationMinutes", 0) or 1) / 60.0, 0.5)
        cost_per_hour = float(cheapest_flight.get("price", 0)) / duration_hours
        modes_for_value.append(("flight", cost_per_hour))

    if trains["applicable"] and trains["options"]:
        train = trains["options"][0]
        if train.get("minPrice") and train.get("durationHours"):
            modes_for_value.append(("train", float(train["minPrice"]) / float(train["durationHours"])))

    if buses["applicable"] and buses["options"]:
        bus = buses["options"][0]
        if bus.get("minPrice") and bus.get("durationHours"):
            modes_for_value.append(("bus", float(bus["minPrice"]) / float(bus["durationHours"])))

    best_value = None
    best_value_reason = "Insufficient comparable transport data"
    if modes_for_value:
        best_value = min(modes_for_value, key=lambda item: item[1])[0]
        best_value_reason = "Cheapest per travel hour"

        value_map = {name: value for name, value in modes_for_value}
        if "flight" in value_map and "bus" in value_map and value_map["flight"] * 3 < value_map["bus"]:
            best_value = "flight"
            best_value_reason = "Flight is >3x cheaper per travel hour than bus"

    return {
        "flights": flight_offers[:3],
        "flightSource": "travelpayouts_live" if flight_offers else (flights_data.get("error_type") or "unavailable"),
        "flightMessage": flights_data.get("message", "") if not flight_offers else "",
        "trains": trains,
        "buses": buses,
        "bestValue": best_value,
        "bestValueReason": best_value_reason,
    }


@tool
def get_transport_options(query: str) -> str:
    """
    Returns transport mode options (flight/train/bus) between cities with estimated prices and travel times.
    Use for domestic Indian routes or when user asks about non-flight transport.
    Input: "FROM_CITY TO_CITY"
    """
    cleaned = " ".join((query or "").strip().split())
    if not cleaned:
        return "Invalid input. Use: 'FROM_CITY TO_CITY'."

    if " to " in cleaned.lower():
        parts = re.split(r"\s+to\s+", cleaned, flags=re.IGNORECASE)
        if len(parts) != 2:
            return "Invalid input. Use: 'FROM_CITY TO_CITY'."
        from_city, to_city = parts[0], parts[1]
    else:
        tokens = cleaned.split()
        if len(tokens) < 2:
            return "Invalid input. Use: 'FROM_CITY TO_CITY'."
        from_city = " ".join(tokens[:-1])
        to_city = tokens[-1]

    data = get_transport_options_data(from_city, to_city)

    lines = [
        f"Transport options from {from_city} to {to_city}:",
        "-" * 55,
    ]

    if data.get("flights"):
        cheapest = min(data["flights"], key=lambda item: item.get("price", float("inf")))
        stop_text = "Direct" if cheapest.get("stops", 0) == 0 else f"{cheapest.get('stops', 0)} stop(s)"
        lines.append(
            f"Flight (Live data): {cheapest.get('airline', 'Airline')} | {cheapest.get('duration', 'N/A')} | "
            f"{stop_text} | {cheapest.get('currency', 'INR')} {cheapest.get('price', 0):,.0f}"
        )
    else:
        message = data.get("flightMessage") or "Live flight pricing unavailable."
        lines.append(f"Flight: {message}")

    if data.get("trains", {}).get("applicable"):
        train = data["trains"]["options"][0]
        source = "Live data" if train.get("source") == "live" else "Estimated range"
        lines.append(
            f"Train ({source}): {train.get('journeyTime')} | {train.get('priceRange')} | {train.get('frequency')}"
        )
    else:
        lines.append("Train: Not applicable for international travel.")

    if data.get("buses", {}).get("applicable"):
        bus = data["buses"]["options"][0]
        source = "Live data" if bus.get("source") == "live" else "Estimated range"
        lines.append(
            f"Bus ({source}): {bus.get('journeyTime')} | {bus.get('priceRange')} | {bus.get('frequency')}"
        )
    else:
        lines.append("Bus: Not applicable for international travel.")

    if data.get("bestValue"):
        lines.append(f"Best value: {data['bestValue']} ({data.get('bestValueReason', 'Cheapest per travel hour')})")

    return "\n".join(lines)


# Compatibility wrapper for older imports
@tool
def get_transport_prices(origin: str, destination: str, date: str, modes: List[str]) -> str:
    data = get_transport_options_data(origin, destination, date)
    mode_map = {
        "flight": data.get("flights", [None])[0],
        "train": (data.get("trains", {}).get("options") or [None])[0],
        "bus": (data.get("buses", {}).get("options") or [None])[0],
    }

    out: Dict[str, Dict] = {}
    for mode in modes or ["flight", "train", "bus"]:
        item = mode_map.get(mode)
        if not item:
            out[mode] = {
                "min_price": 0.0,
                "max_price": 0.0,
                "currency": "INR",
                "source": "Estimate unavailable",
                "booking_url": "",
                "mode": mode,
            }
            continue

        if mode == "flight":
            out[mode] = {
                "min_price": float(item.get("price", 0.0)),
                "max_price": float(item.get("price", 0.0)),
                "currency": item.get("currency", "INR"),
                "source": "Travelpayouts",
                "booking_url": "",
                "mode": mode,
            }
        else:
            min_price = float(item.get("minPrice") or 0.0)
            out[mode] = {
                "min_price": min_price,
                "max_price": min_price,
                "currency": "INR",
                "source": item.get("source", "estimated"),
                "booking_url": "",
                "mode": mode,
            }

    return json.dumps(out)
