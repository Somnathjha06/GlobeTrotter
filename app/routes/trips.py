import json
from datetime import date, datetime

from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, jsonify,
)
from flask_login import login_required, current_user

from app import db
from app.models.city import City
from app.models.activity import Activity
from app.models.trip import Trip, TripStatus
from app.models.trip_stop import TripStop

trips_bp = Blueprint("trips", __name__, template_folder="../templates/trips")

# ---------------------------------------------------------------------------
# Activity seed data — inserted per-city on first need
# ---------------------------------------------------------------------------
ACTIVITY_SEEDS = {
    "Tokyo": [
        {"name": "Visit Senso-ji Temple",        "type": "sightseeing", "cost": 0,    "duration": 2.0},
        {"name": "Tokyo Skytree observation deck","type": "sightseeing", "cost": 20,   "duration": 1.5},
        {"name": "Tsukiji outer market food tour","type": "food",        "cost": 30,   "duration": 2.5},
        {"name": "Shibuya Crossing & Harajuku",   "type": "sightseeing", "cost": 0,    "duration": 3.0},
        {"name": "Robot Restaurant show",          "type": "entertainment","cost": 80,  "duration": 2.0},
        {"name": "Day trip to Nikko",              "type": "adventure",   "cost": 50,   "duration": 8.0},
    ],
    "Paris": [
        {"name": "Eiffel Tower summit visit",     "type": "sightseeing", "cost": 26,   "duration": 2.0},
        {"name": "Louvre Museum",                  "type": "culture",     "cost": 17,   "duration": 4.0},
        {"name": "Seine River dinner cruise",      "type": "food",        "cost": 65,   "duration": 2.5},
        {"name": "Montmartre & Sacré-Cœur walk",  "type": "sightseeing", "cost": 0,    "duration": 3.0},
        {"name": "Versailles Palace & Gardens",    "type": "culture",     "cost": 20,   "duration": 6.0},
        {"name": "French cooking class",           "type": "food",        "cost": 90,   "duration": 3.0},
    ],
    "Bali": [
        {"name": "Tanah Lot temple sunset",        "type": "sightseeing", "cost": 5,    "duration": 2.5},
        {"name": "Ubud Monkey Forest",             "type": "nature",      "cost": 4,    "duration": 1.5},
        {"name": "Mount Batur sunrise trek",       "type": "adventure",   "cost": 35,   "duration": 6.0},
        {"name": "Balinese cooking class",         "type": "food",        "cost": 40,   "duration": 4.0},
        {"name": "Kuta beach surfing lesson",      "type": "adventure",   "cost": 25,   "duration": 2.0},
        {"name": "Traditional Kecak dance show",   "type": "culture",     "cost": 10,   "duration": 1.5},
    ],
    "New York": [
        {"name": "Statue of Liberty & Ellis Island","type": "sightseeing","cost": 24,   "duration": 4.0},
        {"name": "Central Park walking tour",       "type": "sightseeing","cost": 0,    "duration": 2.5},
        {"name": "Metropolitan Museum of Art",      "type": "culture",    "cost": 25,   "duration": 3.0},
        {"name": "Broadway show",                   "type": "entertainment","cost": 120,"duration": 2.5},
        {"name": "NYC pizza crawl in Brooklyn",     "type": "food",       "cost": 40,   "duration": 3.0},
        {"name": "One World Observatory",           "type": "sightseeing","cost": 34,   "duration": 1.5},
    ],
    "Cape Town": [
        {"name": "Table Mountain cable car",       "type": "sightseeing", "cost": 22,   "duration": 3.0},
        {"name": "Cape Point & Boulders Penguins", "type": "nature",      "cost": 18,   "duration": 5.0},
        {"name": "Winelands tour (Stellenbosch)",  "type": "food",        "cost": 60,   "duration": 6.0},
        {"name": "V&A Waterfront seafood dinner",  "type": "food",        "cost": 35,   "duration": 2.0},
        {"name": "Robben Island tour",             "type": "culture",     "cost": 20,   "duration": 4.0},
        {"name": "Shark cage diving",              "type": "adventure",   "cost": 150,  "duration": 5.0},
    ],
}

TYPE_ICONS = {
    "sightseeing":   "🏛️",
    "food":          "🍜",
    "adventure":     "🧗",
    "culture":       "🎭",
    "entertainment": "🎪",
    "nature":        "🌿",
}


def _seed_activities_for_city(city: City) -> None:
    """Insert sample activities for a city if it has none."""
    if city.activities.first() is None:
        seeds = ACTIVITY_SEEDS.get(city.name, [])
        for s in seeds:
            db.session.add(Activity(city_id=city.id, **s))
        db.session.commit()


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _compute_status(trip) -> str:
    """Derive the real status from today's date vs. trip dates.
    Falls back to the stored enum value if dates are missing.
    """
    today = date.today()
    if trip.start_date and trip.end_date:
        if today < trip.start_date:
            return "upcoming"
        elif today > trip.end_date:
            return "completed"
        else:
            return "ongoing"
    elif trip.start_date and today > trip.start_date:
        return "ongoing"
    # Fall back to stored value
    return trip.status.value


# ---------------------------------------------------------------------------
# Trips index — tabbed list with computed status
# ---------------------------------------------------------------------------

@trips_bp.route("/")
@login_required
def index():
    q      = request.args.get("q", "").strip()
    sort   = request.args.get("sort", "newest")
    tab    = request.args.get("tab", "all")    # all | upcoming | ongoing | completed

    trips_q = Trip.query.filter_by(user_id=current_user.id)

    if q:
        trips_q = trips_q.filter(Trip.name.ilike(f"%{q}%"))

    if sort == "oldest":
        trips_q = trips_q.order_by(Trip.id.asc())
    elif sort == "name":
        trips_q = trips_q.order_by(Trip.name.asc())
    elif sort == "start":
        trips_q = trips_q.order_by(Trip.start_date.asc().nullsfirst())
    else:  # newest
        trips_q = trips_q.order_by(Trip.id.desc())

    all_trips = trips_q.all()

    # Attach computed status to every trip object (don't mutate the model enum)
    for trip in all_trips:
        trip.computed_status = _compute_status(trip)

    # Bucket into tabs
    buckets = {
        "ongoing":   [t for t in all_trips if t.computed_status == "ongoing"],
        "upcoming":  [t for t in all_trips if t.computed_status == "upcoming"],
        "completed": [t for t in all_trips if t.computed_status == "completed"],
    }

    # Active tab trips (default "all" shows everything)
    if tab in buckets:
        active_trips = buckets[tab]
    else:
        active_trips = all_trips

    counts = {k: len(v) for k, v in buckets.items()}
    counts["all"] = len(all_trips)

    return render_template(
        "trips_list.html",
        trips=active_trips,
        all_trips=all_trips,
        counts=counts,
        q=q,
        sort=sort,
        tab=tab,
        today=date.today(),
    )



# ---------------------------------------------------------------------------
# Create new trip
# ---------------------------------------------------------------------------

@trips_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    cities = City.query.order_by(City.name).all()

    # Pre-select city from query param (e.g. coming from a city card click)
    preselect_city_id = request.args.get("city_id", type=int)

    if request.method == "POST":
        trip_name  = request.form.get("trip_name", "").strip()
        city_id    = request.form.get("city_id", type=int)
        start_str  = request.form.get("start_date", "")
        end_str    = request.form.get("end_date", "")
        description= request.form.get("description", "").strip()

        errors = []

        if not trip_name:
            errors.append("Trip name is required.")
        if not city_id:
            errors.append("Please select a destination city.")

        start_date = _parse_date(start_str)
        end_date   = _parse_date(end_str)

        if start_str and not start_date:
            errors.append("Invalid start date format.")
        if end_str and not end_date:
            errors.append("Invalid end date format.")
        if start_date and end_date and end_date <= start_date:
            errors.append("End date must be after the start date.")

        if errors:
            for e in errors:
                flash(e, "danger")
            # Re-render with user's filled values
            activities = []
            if city_id:
                city = City.query.get(city_id)
                if city:
                    _seed_activities_for_city(city)
                    activities = city.activities.all()
            return render_template(
                "new_trip.html",
                cities=cities,
                activities=activities,
                selected_city_id=city_id,
                preselect_city_id=city_id,
                form=request.form,
            )

        # ── Create trip ──────────────────────────────────────────────────
        city = City.query.get_or_404(city_id)
        _seed_activities_for_city(city)

        trip = Trip(
            user_id=current_user.id,
            name=trip_name,
            start_date=start_date,
            end_date=end_date,
            description=description or None,
            status=TripStatus.UPCOMING,
        )
        db.session.add(trip)
        db.session.flush()  # get trip.id before commit

        # Create the first TripStop for the chosen city
        stop = TripStop(
            trip_id=trip.id,
            city_id=city.id,
            start_date=start_date,
            end_date=end_date,
            order_index=0,
        )
        db.session.add(stop)
        db.session.commit()

        flash(f'Trip "{trip.name}" created! Start building your itinerary.', "success")
        return redirect(url_for("itinerary.view", trip_id=trip.id))

    # GET — seed activities for preselected city
    activities = []
    if preselect_city_id:
        city = City.query.get(preselect_city_id)
        if city:
            _seed_activities_for_city(city)
            activities = city.activities.all()

    return render_template(
        "new_trip.html",
        cities=cities,
        activities=activities,
        selected_city_id=preselect_city_id,
        preselect_city_id=preselect_city_id,
        form={},
    )


# ---------------------------------------------------------------------------
# AJAX endpoint — activities for a city
# ---------------------------------------------------------------------------

@trips_bp.route("/api/activities/<int:city_id>")
@login_required
def activities_for_city(city_id: int):
    city = City.query.get_or_404(city_id)
    _seed_activities_for_city(city)
    result = [
        {
            "id":       a.id,
            "name":     a.name,
            "type":     a.type or "general",
            "icon":     TYPE_ICONS.get(a.type, "📌"),
            "cost":     a.cost,
            "duration": a.duration,
        }
        for a in city.activities.all()
    ]
    return jsonify(result)


