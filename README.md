# 🇮🇳 India Tourist Guide

India Tourist Guide is a simple full-stack web application that helps tourists explore popular destinations in India.

The website provides information about tourist places, their history, attractions, hotel options, and famous local food.

## Project objective

The goal of this project is to provide tourists with useful introductory information about destinations across India in one place.

## Features

- Search for destinations by name, state, or description
- Browse popular tourist destinations
- Read about each place's history and attractions
- Explore example hotel options
- Discover famous local food
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
   python -m pip install Flask
   ```

3. From the project root, start the application:

   ```bash
   python frontend/backend/app.py
   ```

4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.
