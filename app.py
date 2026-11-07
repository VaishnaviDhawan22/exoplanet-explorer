from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from models import db, Planet, User, Favorite

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///planets.db"
db.init_app(app)
app.secret_key = "change-this-to-any-random-text"

with app.app_context():
    db.create_all()

METHOD_INFO = {
    "Transit": "When a planet passes in front of its star, the star's light dips slightly, like a tiny eclipse. Telescopes measure this dip, and its size reveals the planet's size. This is the most productive method so far, used by the Kepler and TESS space telescopes.",
    "Radial Velocity": "A planet's gravity tugs on its star, making the star wobble slightly. As the star moves toward us its light shifts a little bluer, and as it moves away it shifts redder (the Doppler effect). Measuring this shift reveals the planet's mass and orbit.",
    "Imaging": "The planet is photographed directly. Since the star is far brighter, its light has to be blocked out. This works mostly for large, young planets that orbit far from their star.",
    "Microlensing": "When one star passes in front of another, its gravity bends and magnifies the background star's light like a lens. If the foreground star has a planet, it adds a short extra blip to the signal. The event happens only once and never repeats.",
    "Transit Timing Variations": "If a star has multiple planets, their gravity slightly changes the timing of each other's transits. Tiny timing shifts reveal the presence of an extra, unseen planet.",
    "Eclipse Timing Variations": "Two stars orbit each other and eclipse regularly. If the timing of those eclipses drifts, a planet may be pulling on the pair.",
    "Pulsar Timing": "A pulsar is a spinning dead star that sends out extremely regular pulses. If the pulses arrive slightly early or late, a planet may be tugging on it. The first exoplanets ever found (in 1992) were discovered this way.",
    "Astrometry": "A planet's gravity makes its star shift position very slightly in the sky. Extremely precise measurements can detect this tiny movement.",
    "Orbital Brightness Modulation": "The side of a planet facing its star glows, and as the planet orbits, its brightness changes in a repeating pattern. This small variation reveals the planet.",
}


@app.context_processor
def inject_user():
    return {"current_user": session.get("username")}


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    return redirect(url_for("planets"))


@app.route("/planets")
def planets():
    q = request.args.get("q", "")
    method = request.args.get("method", "")
    year = request.args.get("year", type=int)
    sort = request.args.get("sort", "name")
    page = request.args.get("page", 1, type=int)

    query = Planet.query
    if q:
        query = query.filter(Planet.name.ilike(f"%{q}%"))
    if method:
        query = query.filter(Planet.method == method)
    if year:
        query = query.filter(Planet.discovery_year >= year)

    if sort == "distance":
        query = query.filter(Planet.distance_pc.isnot(None)).order_by(Planet.distance_pc)
    elif sort == "score":
        query = query.order_by(Planet.habitability_score.desc())
    else:
        query = query.order_by(Planet.name)

    pagination = query.paginate(page=page, per_page=25, error_out=False)
    methods = [m[0] for m in db.session.query(Planet.method).distinct().order_by(Planet.method) if m[0]]

    return render_template("planets.html", pagination=pagination, methods=methods,
                           q=q, method=method, year=year, sort=sort)


@app.route("/top")
def top():
    planets = (Planet.query
               .filter(Planet.habitability_score.isnot(None))
               .order_by(Planet.habitability_score.desc())
               .limit(20).all())
    return render_template("top.html", planets=planets)


@app.route("/planet/<int:planet_id>")
def planet_detail(planet_id):
    planet = db.get_or_404(Planet, planet_id)

    earth_rows = [
        ("Radius (Earth = 1)", planet.radius_earth, 1.0),
        ("Mass (Earth = 1)", planet.mass_earth, 1.0),
        ("Orbital period (days)", planet.orbital_period, 365.25),
        ("Temperature (K)", planet.temperature, 288),
    ]

    rows = []
    for label, value, earth_value in earth_rows:
        ratio = round(value / earth_value, 2) if value is not None else None
        rows.append({"label": label, "value": value, "earth": earth_value, "ratio": ratio})

    distance_ly = round(planet.distance_pc * 3.26, 1) if planet.distance_pc else None
    voyager_years = int(distance_ly * 17600) if distance_ly else None
    method_info = METHOD_INFO.get(planet.method, "No explanation is available for this method yet.")

    fav = None
    if "user_id" in session:
        fav = Favorite.query.filter_by(user_id=session["user_id"], planet_id=planet.id).first()

    return render_template("planet_detail.html", planet=planet, rows=rows,
                           distance_ly=distance_ly, voyager_years=voyager_years,
                           method_info=method_info, fav=fav)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or len(password) < 6:
            flash("Username is required and password must be at least 6 characters.")
        elif User.query.filter_by(username=username).first():
            flash("That username is already taken.")
        else:
            user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            flash("Account created! Please log in.")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("planets"))
        flash("Wrong username or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/favorite/<int:planet_id>", methods=["POST"])
@login_required
def toggle_favorite(planet_id):
    fav = Favorite.query.filter_by(user_id=session["user_id"], planet_id=planet_id).first()
    if fav:
        db.session.delete(fav)
        flash("Removed from favorites.")
    else:
        db.session.add(Favorite(user_id=session["user_id"], planet_id=planet_id))
        flash("Added to favorites!")
    db.session.commit()
    return redirect(url_for("planet_detail", planet_id=planet_id))


@app.route("/note/<int:planet_id>", methods=["POST"])
@login_required
def save_note(planet_id):
    fav = Favorite.query.filter_by(user_id=session["user_id"], planet_id=planet_id).first()
    if fav:
        fav.note = request.form["note"]
        db.session.commit()
        flash("Note saved.")
    return redirect(url_for("planet_detail", planet_id=planet_id))


@app.route("/favorites")
@login_required
def favorites():
    favs = Favorite.query.filter_by(user_id=session["user_id"]).all()
    return render_template("favorites.html", favs=favs)


@app.route("/charts")
def charts():
    by_year = (db.session.query(Planet.discovery_year, func.count(Planet.id))
               .filter(Planet.discovery_year.isnot(None))
               .group_by(Planet.discovery_year)
               .order_by(Planet.discovery_year).all())
    by_method = (db.session.query(Planet.method, func.count(Planet.id))
                 .filter(Planet.method.isnot(None))
                 .group_by(Planet.method)
                 .order_by(func.count(Planet.id).desc()).all())
    return render_template("charts.html",
                           years=[y for y, _ in by_year],
                           year_counts=[c for _, c in by_year],
                           methods=[m for m, _ in by_method],
                           method_counts=[c for _, c in by_method])


def planet_to_dict(p):
    return {
        "id": p.id, "name": p.name, "host_star": p.host_star,
        "discovery_year": p.discovery_year, "method": p.method,
        "radius_earth": p.radius_earth, "mass_earth": p.mass_earth,
        "orbital_period_days": p.orbital_period, "temperature_k": p.temperature,
        "distance_pc": p.distance_pc, "habitability_score": p.habitability_score,
    }


@app.route("/api/planets")
def api_planets():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    pag = Planet.query.order_by(Planet.name).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "page": pag.page, "pages": pag.pages, "total": pag.total,
        "planets": [planet_to_dict(p) for p in pag.items],
    })


@app.route("/api/planets/<int:planet_id>")
def api_planet(planet_id):
    return jsonify(planet_to_dict(db.get_or_404(Planet, planet_id)))


if __name__ == "__main__":
    app.run(debug=True)