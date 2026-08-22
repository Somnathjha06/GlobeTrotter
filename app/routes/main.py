from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from app import db
from app.models.city import City
from app.models.trip import Trip

main_bp = Blueprint("main", __name__, template_folder="../templates/main")

# ---------------------------------------------------------------------------
# Seed data — inserted once if the cities table is empty
# ---------------------------------------------------------------------------
SEED_CITIES = [
    {"name": "Tokyo",       "country": "Japan",        "cost_index": 1.6,  "popularity": 98},
    {"name": "Paris",       "country": "France",       "cost_index": 1.8,  "popularity": 95},
    {"name": "Bali",        "country": "Indonesia",    "cost_index": 0.7,  "popularity": 92},
    {"name": "New York",    "country": "USA",          "cost_index": 2.1,  "popularity": 97},
    {"name": "Cape Town",   "country": "South Africa", "cost_index": 0.9,  "popularity": 88},
]

CITY_EMOJIS = {
    "Tokyo":    "🗼", "Paris":    "🗼", "Bali": "🌴",
    "New York": "🗽", "Cape Town": "🌊",
}

CITY_TAGLINES = {
    "Tokyo":    "Neon lights & ancient shrines",
    "Paris":    "Art, cuisine & the Eiffel Tower",
    "Bali":     "Tropical paradise & spiritual retreat",
    "New York": "The city that never sleeps",
    "Cape Town":"Where mountains meet the ocean",
}


def _ensure_cities_seeded() -> None:
    """Seed sample cities if the table is empty."""
    if City.query.first() is None:
        for data in SEED_CITIES:
            db.session.add(City(**data))
        db.session.commit()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@main_bp.route("/dashboard")
@login_required
def dashboard():
    _ensure_cities_seeded()

    # Search query (against trip name)
    q      = request.args.get("q", "").strip()
    sort   = request.args.get("sort", "newest")
    status = request.args.get("status", "all")
    group  = request.args.get("group", "none")

    # Build trips query for current user
    trips_q = Trip.query.filter_by(user_id=current_user.id)

    if q:
        trips_q = trips_q.filter(Trip.name.ilike(f"%{q}%"))

    if status != "all":
        trips_q = trips_q.filter(Trip.status == status)

    if sort == "oldest":
        trips_q = trips_q.order_by(Trip.id.asc())
    elif sort == "name":
        trips_q = trips_q.order_by(Trip.name.asc())
    elif sort == "start":
        trips_q = trips_q.order_by(Trip.start_date.asc())
    else:  # newest
        trips_q = trips_q.order_by(Trip.id.desc())

    trips = trips_q.all()

    # Top cities by popularity
    top_cities = City.query.order_by(City.popularity.desc()).limit(5).all()

    # Attach display helpers
    for city in top_cities:
        city.emoji   = CITY_EMOJIS.get(city.name, "🏙️")
        city.tagline = CITY_TAGLINES.get(city.name, "Discover this destination")

    return render_template(
        "dashboard.html",
        trips=trips,
        top_cities=top_cities,
        q=q,
        sort=sort,
        status=status,
        group=group,
    )
