import pandas as pd
from app import app
from models import db, Planet

df = pd.read_csv("data/planets.csv")
df = df.astype(object).where(pd.notnull(df), None)

def to_int(x):
    return int(x) if x is not None else None

with app.app_context():
    db.drop_all()
    db.create_all()
    for _, r in df.iterrows():
        db.session.add(Planet(
            name=r["pl_name"],
            host_star=r["hostname"],
            discovery_year=to_int(r["disc_year"]),
            method=r["discoverymethod"],
            radius_earth=r["pl_rade"],
            mass_earth=r["pl_masse"],
            orbital_period=r["pl_orbper"],
            temperature=r["pl_eqt"],
            distance_pc=r["sy_dist"],
        ))
    db.session.commit()
    print("Planets imported:", Planet.query.count())