from app import app
from models import db, Planet

def calc_score(p):
    if p.radius_earth is None or p.temperature is None:
        return None
    size_score = max(0, 1 - abs(p.radius_earth - 1) / 1.5)
    temp_score = max(0, 1 - abs(p.temperature - 288) / 100)
    return round((0.5 * size_score + 0.5 * temp_score) * 100, 1)

with app.app_context():
    for p in Planet.query.all():
        p.habitability_score = calc_score(p)
    db.session.commit()
    count = Planet.query.filter(Planet.habitability_score.isnot(None)).count()
    print("Scores calculated:", count)