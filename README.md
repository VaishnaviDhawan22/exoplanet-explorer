# 🚀 Exoplanet Explorer

A full-stack web application to explore 5,800+ confirmed exoplanets from the NASA Exoplanet Archive. It includes a custom habitability scoring algorithm, user accounts, interactive charts and a 3D size comparison for every planet.

## 🖼️ Screenshots

### All planets (search, filters, sorting)
![Planets list](screenshots/planets.png)

### Planet detail (Earth comparison, 3D visual, discovery method)
![Planet detail 1](screenshots/detail1.png)
![Planet detail 2](screenshots/detail2.png)

## ✨ Features

- **Browse & search** thousands of planets with filters (discovery method, year), sorting (nearest first, most habitable) and pagination
- **Habitability score (0-100)** calculated from a planet's size and temperature compared to Earth
- **Top 20** most habitable planets leaderboard
- **Planet detail page** with distance in light years, comparison with Earth, and a plain-English explanation of how it was discovered
- **Interactive 3D visual** (Three.js) comparing the planet's size with Earth, coloured by temperature
- **User accounts**: sign up, log in, log out with securely hashed passwords
- **Favorites and personal notes** for each planet
- **Charts** (Chart.js): planets discovered per year and discovery methods
- **REST API** returning JSON: `/api/planets` and `/api/planets/<id>`

## 🛠️ Tech Stack

| Area | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite, SQLAlchemy (ORM) |
| Data processing | pandas |
| Frontend | HTML, CSS, Bootstrap, Jinja2 templates |
| JavaScript | Chart.js, Three.js |

## 🧮 How the habitability score works

Score = 50% size similarity to Earth + 50% temperature similarity to Earth (288 K), scaled from 0 to 100. Planets that are Earth-sized and have a temperate climate score highest. Most discovered planets (large, very hot gas giants) score close to 0, and planets with missing data have no score.

## ▶️ Run locally

1. Clone the repository and open the folder
2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Download the planet data from the NASA Exoplanet Archive as CSV and save it as `data/planets.csv`
5. Load the data and calculate scores
   ```bash
   python import.py
   python score.py
   ```
6. Start the app
   ```bash
   python app.py
   ```
7. Open http://127.0.0.1:5000 in your browser

## 📡 API example

`GET /api/planets?page=1&per_page=20` returns paginated JSON with each planet's name, host star, discovery year, method, radius, mass, temperature, distance and habitability score.

## 🗂️ Project structure

```
exoplanet-explorer/
├── app.py            # Flask routes and logic
├── models.py         # Database models (Planet, User, Favorite)
├── import.py         # Loads the CSV into the database
├── score.py          # Calculates habitability scores
├── templates/        # HTML pages (Jinja2)
├── data/             # planets.csv
└── requirements.txt
```

## 👩‍💻 Author

Vaishnavi Dhawan