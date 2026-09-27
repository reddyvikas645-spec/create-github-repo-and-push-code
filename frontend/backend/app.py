from pathlib import Path

from flask import Flask, abort, render_template, request

BASE_DIR = Path(__file__).resolve().parent.parent
app = Flask(__name__, template_folder=str(BASE_DIR), static_folder=str(BASE_DIR))

PLACES = [
    {
        "id": 1,
        "name": "Taj Mahal",
        "state": "Uttar Pradesh",
        "description": "A marble mausoleum and one of the most iconic symbols of India.",
        "history": "Built by Emperor Shah Jahan in memory of Mumtaz Mahal, it is a masterpiece of Mughal architecture.",
        "attractions": "Main mausoleum, reflecting pools, gardens, and nearby Agra Fort.",
        "hotel": "The Oberoi Amarvilas, ITC Mughal, and many budget-friendly guesthouses nearby.",
        "food": "Try Mughlai dishes like biryani, kebabs, and sweet petha in Agra.",
    },
    {
        "id": 2,
        "name": "Jaipur",
        "state": "Rajasthan",
        "description": "The Pink City is famous for its forts, palaces, and vibrant culture.",
        "history": "Founded by Maharaja Sawai Jai Singh II, Jaipur flourished as a royal and strategic city.",
        "attractions": "Hawa Mahal, Amer Fort, City Palace, and Jantar Mantar.",
        "hotel": "Umaid Mahal, The Raj Palace, and comfortable boutique hotels in the old city.",
        "food": "Enjoy dal bati churma, ghevar, and Rajasthani thali.",
    },
    {
        "id": 3,
        "name": "Kerala Backwaters",
        "state": "Kerala",
        "description": "A scenic network of lagoons, canals, and lush landscapes.",
        "history": "The backwaters have shaped local livelihoods and culture for centuries through trade and farming.",
        "attractions": "Houseboat rides, Alleppey canals, Vembanad Lake, and village walks.",
        "hotel": "Luxury houseboats, heritage resorts, and eco-friendly stays in Alleppey and Kumarakom.",
        "food": "Try appam, stew, Kerala sadya, and fresh seafood.",
    },
    {
        "id": 4,
        "name": "Varanasi",
        "state": "Uttar Pradesh",
        "description": "A sacred city with ghats, temples, and timeless spiritual energy.",
        "history": "Believed to be one of the oldest continuously inhabited cities in the world.",
        "attractions": "Ganga Aarti, Dashashwamedh Ghat, Kashi Vishwanath Temple, and boat rides.",
        "hotel": "Boutique guesthouses, riverside hotels, and heritage stays near the ghats.",
        "food": "Sample kachori sabzi, malaiyyo, and Banarasi sweets.",
    },
    {
        "id": 5,
        "name": "Goa",
        "state": "Goa",
        "description": "Known for beaches, night life, Portuguese heritage, and coastal scenery.",
        "history": "Goa was shaped by Portuguese rule and later became a famous beach destination.",
        "attractions": "Baga Beach, Old Goa churches, Dudhsagar Falls, and Panaji markets.",
        "hotel": "Beach resorts, boutique homestays, and family-friendly hotels across North and South Goa.",
        "food": "Try Goan fish curry, bebinca, and sorpotel.",
    },
]


@app.route("/")
def home():
    search_query = (request.args.get("search") or "").strip()

    if search_query:
        filtered_places = [
            place for place in PLACES
            if search_query.lower() in " ".join(
                [place["name"], place["state"], place["description"]]
            ).lower()
        ]
    else:
        filtered_places = PLACES

    return render_template("index.html", places=filtered_places, search=search_query)


@app.route("/place/<int:place_id>")
def place_detail(place_id):
    place = next((item for item in PLACES if item["id"] == place_id), None)
    if place is None:
        abort(404)
    return render_template("place.html", place=place)


@app.errorhandler(404)
def page_not_found(_error):
    return "Page not found.", 404


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
