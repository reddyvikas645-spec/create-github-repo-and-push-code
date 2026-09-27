import html
import json
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, abort, render_template, request, url_for

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, template_folder=BASE_DIR, static_folder=BASE_DIR)

PLACE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "name": {"type": "STRING"},
        "state": {"type": "STRING"},
        "description": {"type": "STRING"},
        "history": {"type": "STRING"},
        "attractions": {"type": "ARRAY", "items": {"type": "STRING"}},
        "hotel": {"type": "ARRAY", "items": {"type": "STRING"}},
        "food": {"type": "ARRAY", "items": {"type": "STRING"}},
        "best_time": {"type": "STRING"},
        "itinerary": {
            "type": "OBJECT",
            "properties": {
                "day_1": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "time": {"type": "STRING"},
                            "activity": {"type": "STRING"},
                        },
                        "required": ["time", "activity"],
                    },
                },
                "day_2": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "time": {"type": "STRING"},
                            "activity": {"type": "STRING"},
                        },
                        "required": ["time", "activity"],
                    },
                },
            },
            "required": ["day_1", "day_2"],
        },
        "travel_tips": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": [
        "name", "state", "description", "history", "attractions",
        "hotel", "food", "best_time", "itinerary", "travel_tips",
    ],
}

PLACES = [
    {
        "id": 1,
        "name": "Taj Mahal",
        "state": "Uttar Pradesh",
        "description": "A marble mausoleum and one of the most iconic symbols of India.",
        "history": "Built by Emperor Shah Jahan in memory of Mumtaz Mahal, it is a masterpiece of Mughal architecture.",
        "attractions": ["Main mausoleum", "Reflecting pools", "Mughal gardens", "Nearby Agra Fort"],
        "hotel": ["The Oberoi Amarvilas", "ITC Mughal", "Budget-friendly guesthouses in Agra"],
        "food": ["Mughlai biryani", "Kebabs", "Agra petha"],
        "best_time": "October to March, when Agra is generally cooler.",
        "itinerary": {
            "day_1": [
                {"time": "Sunrise", "activity": "Visit the Taj Mahal in the cooler early hours."},
                {"time": "Late morning", "activity": "Explore Agra Fort, a short drive from the Taj."},
                {"time": "Evening", "activity": "See the Taj Mahal from Mehtab Bagh across the Yamuna."},
            ],
            "day_2": [
                {"time": "Morning", "activity": "Visit the Tomb of Itimad-ud-Daulah."},
                {"time": "Afternoon", "activity": "Explore local crafts and sample Agra petha."},
            ],
        },
        "travel_tips": ["Check current monument opening days and ticket rules before travelling.", "Allow extra time for security checks at the Taj Mahal."],
    },
    {
        "id": 2,
        "name": "Jaipur",
        "state": "Rajasthan",
        "description": "The Pink City is famous for its forts, palaces, and vibrant culture.",
        "history": "Founded by Maharaja Sawai Jai Singh II, Jaipur flourished as a royal and strategic city.",
        "attractions": ["Hawa Mahal", "Amer Fort", "City Palace", "Jantar Mantar"],
        "hotel": ["Umaid Mahal", "The Raj Palace", "Boutique hotels in the old city"],
        "food": ["Dal bati churma", "Ghevar", "Rajasthani thali"],
        "best_time": "October to March, when daytime sightseeing is more comfortable.",
        "itinerary": {
            "day_1": [
                {"time": "Morning", "activity": "Explore Amer Fort; arrive early to avoid the busiest hours."},
                {"time": "Afternoon", "activity": "Visit Hawa Mahal and the nearby City Palace."},
                {"time": "Evening", "activity": "Walk through the old city markets and try a Rajasthani thali."},
            ],
            "day_2": [
                {"time": "Morning", "activity": "Visit Jantar Mantar and learn about its astronomical instruments."},
                {"time": "Afternoon", "activity": "See Albert Hall Museum or explore a local craft market."},
            ],
        },
        "travel_tips": ["Carry water and sun protection for fort visits.", "Use licensed taxis or app-based transport for longer trips around the city."],
    },
    {
        "id": 3,
        "name": "Kerala Backwaters",
        "state": "Kerala",
        "description": "A scenic network of lagoons, canals, and lush landscapes.",
        "history": "The backwaters have shaped local livelihoods and culture for centuries through trade and farming.",
        "attractions": ["Houseboat rides", "Alleppey canals", "Vembanad Lake", "Village walks"],
        "hotel": ["Houseboats", "Heritage resorts", "Eco-friendly stays in Alleppey and Kumarakom"],
        "food": ["Appam and stew", "Kerala sadya", "Fresh seafood"],
        "best_time": "November to February for drier, milder weather.",
        "itinerary": {
            "day_1": [
                {"time": "Morning", "activity": "Board a houseboat in Alleppey and cruise the canals."},
                {"time": "Afternoon", "activity": "Enjoy a locally prepared lunch and watch village life along the waterways."},
                {"time": "Evening", "activity": "Stay overnight on the houseboat or at a backwater homestay."},
            ],
            "day_2": [
                {"time": "Morning", "activity": "Take a quiet canoe ride through narrower village canals."},
                {"time": "Afternoon", "activity": "Visit a local village or lakeside market before departing."},
            ],
        },
        "travel_tips": ["Confirm what meals and transfers are included before booking a houseboat.", "Monsoon conditions can affect boat schedules; check locally."],
    },
    {
        "id": 4,
        "name": "Varanasi",
        "state": "Uttar Pradesh",
        "description": "A sacred city with ghats, temples, and timeless spiritual energy.",
        "history": "Believed to be one of the oldest continuously inhabited cities in the world.",
        "attractions": ["Ganga Aarti", "Dashashwamedh Ghat", "Kashi Vishwanath Temple", "Boat rides on the Ganges"],
        "hotel": ["Boutique guesthouses", "Riverside hotels", "Heritage stays near the ghats"],
        "food": ["Kachori sabzi", "Malaiyyo (seasonal)", "Banarasi sweets"],
        "best_time": "October to March for cooler weather; summers can be very hot.",
        "itinerary": {
            "day_1": [
                {"time": "Sunrise", "activity": "Take a boat ride on the Ganges and see the riverfront ghats."},
                {"time": "Late morning", "activity": "Walk through the old city and visit Kashi Vishwanath Temple."},
                {"time": "Evening", "activity": "Watch the Ganga Aarti from a ghat or boat."},
            ],
            "day_2": [
                {"time": "Morning", "activity": "Explore quieter ghats and sample a local breakfast."},
                {"time": "Afternoon", "activity": "Visit Sarnath, an important Buddhist pilgrimage site near Varanasi."},
            ],
        },
        "travel_tips": ["Dress respectfully at religious sites and follow local photography rules.", "The old-city lanes are narrow; plan to walk for some journeys."],
    },
    {
        "id": 5,
        "name": "Goa",
        "state": "Goa",
        "description": "Known for beaches, nightlife, Portuguese heritage, and coastal scenery.",
        "history": "Goa was shaped by Portuguese rule and later became a famous beach destination.",
        "attractions": ["Baga Beach", "Old Goa churches", "Dudhsagar Falls", "Panaji markets"],
        "hotel": ["Beach resorts", "Boutique homestays", "Family-friendly hotels in North and South Goa"],
        "food": ["Goan fish curry", "Bebinca", "Sorpotel"],
        "best_time": "November to February for drier weather and beach activities.",
        "itinerary": {
            "day_1": [
                {"time": "Morning", "activity": "Explore Old Goa's historic churches and heritage sites."},
                {"time": "Afternoon", "activity": "Have a Goan lunch and stroll through Panaji's Latin Quarter."},
                {"time": "Evening", "activity": "Relax at a nearby beach and watch the sunset."},
            ],
            "day_2": [
                {"time": "Morning", "activity": "Choose a North Goa or South Goa beach day."},
                {"time": "Afternoon", "activity": "Visit a local market and try regional Goan dishes."},
            ],
        },
        "travel_tips": ["Check seasonal access and local advisories before visiting Dudhsagar Falls.", "Use licensed transport and follow beach safety flags."],
    },
]

_IMAGE_CACHE = {}
_IMAGE_CACHE_LOCK = threading.Lock()


class GeminiAPIError(Exception):
    pass


class _HTMLTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def _plain_text(value):
    parser = _HTMLTextParser()
    parser.feed(html.unescape(value or ""))
    return " ".join(" ".join(parser.parts).split())


def _gemini_json(prompt, schema):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiAPIError("AI search is not configured yet. Add GEMINI_API_KEY to the server environment.")

    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema,
            "temperature": 0.3,
        },
    }
    req = Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urlopen(req, timeout=18) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 429:
            raise GeminiAPIError("AI search is temporarily rate limited. Please try again shortly.") from error
        raise GeminiAPIError(f"AI search failed (HTTP {error.code}). Please try again.") from error
    except (URLError, TimeoutError) as error:
        raise GeminiAPIError("AI search could not connect. Check the server connection and try again.") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise GeminiAPIError("AI search returned an unreadable response. Please try again.") from error

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        raise GeminiAPIError("AI search returned incomplete place details. Please try again.") from error


def _as_list(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _normalize_place(place):
    normalized = dict(place)
    normalized["name"] = str(normalized.get("name") or "").strip()
    normalized["state"] = str(normalized.get("state") or "").strip()
    for field in ("description", "history", "best_time"):
        normalized[field] = str(normalized.get(field) or "").strip()
    for field in ("attractions", "hotel", "food", "travel_tips"):
        normalized[field] = _as_list(normalized.get(field))
    itinerary = normalized.get("itinerary")
    if not isinstance(itinerary, dict):
        itinerary = {}
    normalized["itinerary"] = {
        day: [
            {
                "time": str(stop.get("time") or "").strip(),
                "activity": str(stop.get("activity") or "").strip(),
            }
            for stop in itinerary.get(day, [])
            if isinstance(stop, dict) and (stop.get("time") or stop.get("activity"))
        ]
        if isinstance(itinerary.get(day), list)
        else []
        for day in ("day_1", "day_2")
    }
    return normalized


def _search_gemini(query):
    schema = {
        "type": "OBJECT",
        "properties": {
            "places": {
                "type": "ARRAY",
                "items": PLACE_SCHEMA,
            }
        },
        "required": ["places"],
    }
    prompt = (
        "Find the distinct tourist destinations in India that best match the user's search. "
        "Return up to 12 relevant, real destinations, not repeated variations of the same place. "
        "For a city or region, include its distinct notable visitor destinations; for a named "
        "monument, return that place and nearby destinations only when genuinely relevant. "
        "Give concise factual summaries, history, attractions, example accommodation areas or "
        "well-known options, local foods, best season, a practical two-day itinerary with time "
        "of day and activity, and useful visitor tips. Do not invent current prices, opening "
        "hours, or availability. If the search is not a place in India, return an empty list. "
        f"User search: {query}"
    )
    response = _gemini_json(prompt, schema)
    places = response.get("places")
    if not isinstance(places, list):
        raise GeminiAPIError("AI search returned an invalid destination list.")
    return [
        normalized
        for normalized in (_normalize_place(place) for place in places if isinstance(place, dict))
        if normalized["name"]
    ]


def _local_matches(query):
    needle = query.casefold()
    fields = ("name", "state", "description", "history")
    matches = []
    for place in PLACES:
        searchable = " ".join(
            [str(place.get(field, "")) for field in fields]
            + place["attractions"] + place["food"]
        ).casefold()
        if needle in searchable:
            matches.append(_normalize_place(place))
    return matches


def _photo_for_place(place):
    cache_key = f"{place['name']}|{place.get('state', '')}".casefold()
    with _IMAGE_CACHE_LOCK:
        if cache_key in _IMAGE_CACHE:
            return _IMAGE_CACHE[cache_key]

    params = urlencode({
        "action": "query",
        "generator": "search",
        "gsrnamespace": 6,
        "gsrsearch": f'{place["name"]} {place.get("state", "")} India',
        "gsrlimit": 8,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": 1400,
        "format": "json",
        "formatversion": 2,
    })
    req = Request(
        f"https://commons.wikimedia.org/w/api.php?{params}",
        headers={"User-Agent": "IndiaTouristGuide/1.0 (destination image lookup)"},
    )
    try:
        with urlopen(req, timeout=7) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise RuntimeError(f"Wikimedia image lookup failed (HTTP {error.code}).") from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError("Wikimedia image lookup could not connect.") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise RuntimeError("Wikimedia image lookup returned unreadable data.") from error

    if not isinstance(result, dict):
        raise RuntimeError("Wikimedia image lookup returned invalid data.")
    pages = result.get("query", {}).get("pages", [])
    if isinstance(pages, dict):
        pages = list(pages.values())
    excluded = re.compile(r"\b(map|logo|flag|coat of arms|location)\b", re.IGNORECASE)
    photo = None
    for page in sorted(pages, key=lambda item: item.get("index", 0)):
        title = page.get("title", "")
        image_info = (page.get("imageinfo") or [{}])[0]
        metadata = image_info.get("extmetadata", {})
        license_name = _plain_text(metadata.get("LicenseShortName", {}).get("value", ""))
        image_url = image_info.get("thumburl") or image_info.get("url")
        source_url = page.get("canonicalurl") or image_info.get("descriptionurl")
        if excluded.search(title) or not image_url or not source_url or not license_name:
            continue
        photo = {
            "url": image_url,
            "source_url": source_url,
            "title": title.removeprefix("File:"),
            "artist": _plain_text(metadata.get("Artist", {}).get("value", "")) or "Wikimedia Commons contributor",
            "license": license_name,
        }
        break

    with _IMAGE_CACHE_LOCK:
        _IMAGE_CACHE[cache_key] = photo
    return photo


def _add_photos(places):
    if not places:
        return False

    failures = 0
    with ThreadPoolExecutor(max_workers=min(8, len(places))) as executor:
        futures = {executor.submit(_photo_for_place, place): place for place in places}
        for future, place in futures.items():
            try:
                place["photo"] = future.result()
            except RuntimeError:
                place["photo"] = None
                failures += 1
    return failures == len(places)


def _place_by_id(place_id):
    return next((place for place in PLACES if place["id"] == place_id), None)


@app.route("/")
def home():
    search_query = (request.args.get("search") or "").strip()[:160]
    search_error = None
    if search_query:
        places_by_name = {
            (place["name"].casefold(), place.get("state", "").casefold()): place
            for place in _local_matches(search_query)
        }
        try:
            for place in _search_gemini(search_query):
                key = (place["name"].casefold(), place.get("state", "").casefold())
                places_by_name.setdefault(key, place)
        except GeminiAPIError as error:
            search_error = str(error)
        places = list(places_by_name.values())
    else:
        places = [_normalize_place(place) for place in PLACES]

    photo_error = _add_photos(places)
    return render_template(
        "index.html",
        places=places,
        search=search_query,
        search_error=search_error,
        photo_error=photo_error,
    )


@app.route("/place/<int:place_id>")
def place_detail(place_id):
    place = _place_by_id(place_id)
    if place is None:
        abort(404)
    normalized_place = _normalize_place(place)
    try:
        normalized_place["photo"] = _photo_for_place(normalized_place)
    except RuntimeError:
        normalized_place["photo"] = None
    return render_template("place.html", place=normalized_place, ai_error=None)


@app.route("/place")
def generated_place_detail():
    name = (request.args.get("name") or "").strip()[:120]
    state = (request.args.get("state") or "").strip()[:120]
    if not name:
        abort(404)

    matches = [
        _normalize_place(place)
        for place in PLACES
        if place["name"].casefold() == name.casefold()
        and (not state or place["state"].casefold() == state.casefold())
    ]
    if matches:
        place = matches[0]
        ai_error = None
    else:
        prompt = (
            "Create a factual, practical visitor guide for this real tourist destination in India. "
            "Include a concise overview and history, attractions, example accommodation options, "
            "local foods, the best season, a realistic two-day itinerary organized by time of day, "
            "and useful travel tips. Do not invent current prices, opening hours, or availability. "
            f"Destination: {name}; state or region: {state or 'identify the correct region'}."
        )
        try:
            place = _normalize_place(_gemini_json(prompt, PLACE_SCHEMA))
            if not place.get("name"):
                place["name"] = name
            if not place.get("state"):
                place["state"] = state
            ai_error = None
        except GeminiAPIError as error:
            place = _normalize_place({
                "name": name,
                "state": state or "India",
                "description": "A destination returned by your search.",
                "history": "",
                "attractions": [],
                "hotel": [],
                "food": [],
                "best_time": "",
                "itinerary": {"day_1": [], "day_2": []},
                "travel_tips": [],
            })
            ai_error = str(error)

    try:
        place["photo"] = _photo_for_place(place)
    except RuntimeError:
        place["photo"] = None
    return render_template("place.html", place=place, ai_error=ai_error)


@app.errorhandler(404)
def page_not_found(_error):
    return "Page not found.", 404


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
