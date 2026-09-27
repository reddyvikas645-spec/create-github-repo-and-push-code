# 🇮🇳 India Tourist Guide

India Tourist Guide is a simple full-stack web application that helps tourists explore popular destinations in India.

The website provides information about tourist places, their history, attractions, hotel options, and famous local food.

## Project objective

The goal of this project is to provide tourists with useful introductory information about destinations across India in one place.

## Features

- Search for destinations by name, state, or description
- Find additional destinations with Gemini-powered search
- Browse popular tourist destinations
- View Wikimedia Commons photos with contributor and license credits
- Read about each place's history and attractions
- Explore example hotel options
- Discover famous local food
- Get a two-day itinerary, best travel season, and visitor tips
- Responsive layout for mobile and desktop

## Technologies

- **Frontend:** HTML and CSS, rendered with Flask templates
- **Backend:** Python and Flask
- **Destination data:** Currently defined in the Flask application

> SQLite is not currently connected to the application. Destination data is stored in the `PLACES` list in `frontend/backend/app.py`.

## Project structure

```text
.
├── frontend/
│   ├── backend/
│   │   └── app.py
│   ├── index.html
│   ├── place.html
│   └── style.css
├── .gitignore
└── README.md
```

## Run locally

1. Install Python 3.
2. Install Flask:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. From the project root, start the application:

   ```bash
   python frontend/backend/app.py
   ```

4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

For AI destination search and generated destination guides, copy `.env.example`
to `.env` and set `GEMINI_API_KEY` to your Google AI Studio API key. The key is
read only by the Flask server; never put it in HTML or commit it. Without the
key, curated destinations and their itineraries remain available, but searches
outside that curated list will not be generated.

## Deploy to Vercel

This repository includes a Vercel Python function entry point and routing
configuration. Import the GitHub repository into Vercel and deploy it with the
repository root as the project root. Vercel will install the dependencies from
`requirements.txt`; pushes to the connected branch can then trigger new
deployments automatically. In the Vercel project's **Settings → Environment
Variables**, add `GEMINI_API_KEY` with your rotated Google AI Studio key, then
redeploy. Keep the key out of Git and client-side code.
