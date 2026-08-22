import json
from datetime import datetime

from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, jsonify, abort,
)
from flask_login import login_required, current_user

from app import db
from app.models.city import City
from app.models.trip import Trip, TripStatus
from app.models.trip_stop import TripStop
from app.models.budget import Budget
from app.models.activity import Activity
from app.models.trip_activity import TripActivity

itinerary_bp = Blueprint(
    "itinerary", __name__, template_folder="../templates/itinerary"
)

TYPE_ICONS = {
    "sightseeing":   "🏛️",
    "food":          "🍜",
    "adventure":     "🧗",
    "culture":       "🎭",
    "entertainment": "🎪",
    "nature":        "🌿",
}


def _parse_date(value: str):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _get_own_trip(trip_id: int) -> Trip:
    """Return the trip or 404; also enforce ownership."""
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first_or_404()
    return trip


# ---------------------------------------------------------------------------
# Main itinerary builder
# ---------------------------------------------------------------------------

@itinerary_bp.route("/trips/<int:trip_id>/itinerary")
@login_required
def view(trip_id: int):
    trip    = _get_own_trip(trip_id)
    cities  = City.query.order_by(City.name).all()
    stops   = trip.stops.all()   # ordered by order_index

    # Attach activity data to each stop
    for stop in stops:
        acts = stop.city.activities.all()
        for a in acts:
            a.icon = TYPE_ICONS.get(a.type, "📌")
        stop.all_activities = acts

        # Which activities are already checked for this stop?
        saved_ids = {ta.activity_id for ta in stop.trip_activities.all()}
        for a in acts:
            a.is_selected = (a.id in saved_ids)

        # Budget for this stop (category = stop city name, or fall back)
        budget = Budget.query.filter_by(
            trip_id=trip_id, category=f"stop_{stop.id}"
        ).first()
        stop.budget = budget

    # Trip-level budgets (not tied to a specific stop)
    trip_budgets = Budget.query.filter(
        Budget.trip_id == trip_id,
        ~Budget.category.like("stop_%"),
    ).all()

    return render_template(
        "builder.html",
        trip=trip,
        stops=stops,
        cities=cities,
        trip_budgets=trip_budgets,
    )


# ---------------------------------------------------------------------------
# Save all sections
# ---------------------------------------------------------------------------

@itinerary_bp.route("/trips/<int:trip_id>/itinerary/save", methods=["POST"])
@login_required
def save(trip_id: int):
    trip = _get_own_trip(trip_id)

    # ── Parse JSON payload sent from JS ──────────────────────────────────
    try:
        payload = request.get_json(force=True, silent=True) or {}
        sections = payload.get("sections", [])
    except Exception:
        return jsonify({"ok": False, "error": "Invalid payload"}), 400

    if not sections:
        return jsonify({"ok": False, "error": "No sections provided"}), 400

    # ── Validate ──────────────────────────────────────────────────────────
    errors = []
    for i, s in enumerate(sections, 1):
        city_id = s.get("city_id")
        if not city_id:
            errors.append(f"Section {i}: city is required.")
        start = _parse_date(s.get("start_date", ""))
        end   = _parse_date(s.get("end_date", ""))
        if start and end and end <= start:
            errors.append(f"Section {i}: end date must be after start date.")

    if errors:
        return jsonify({"ok": False, "errors": errors}), 422

    # ── Wipe existing stops (cascade deletes TripActivities + stop budgets) ─
    # We rebuild from scratch so order_index is always clean.
    TripActivity.query.filter(
        TripActivity.trip_stop_id.in_(
            db.session.query(TripStop.id).filter_by(trip_id=trip_id)
        )
    ).delete(synchronize_session="fetch")

    Budget.query.filter(
        Budget.trip_id == trip_id,
        Budget.category.like("stop_%"),
    ).delete(synchronize_session="fetch")

    TripStop.query.filter_by(trip_id=trip_id).delete()
    db.session.flush()

    # ── Re-insert ──────────────────────────────────────────────────────────
    total_budget = 0.0

    for idx, s in enumerate(sections):
        city_id    = int(s["city_id"])
        start_date = _parse_date(s.get("start_date", ""))
        end_date   = _parse_date(s.get("end_date", ""))
        description = s.get("description", "").strip() or None
        budget_val  = float(s["budget"]) if s.get("budget") else None
        activity_ids = [int(a) for a in s.get("activity_ids", []) if a]

        stop = TripStop(
            trip_id=trip_id,
            city_id=city_id,
            start_date=start_date,
            end_date=end_date,
            description=description,
            order_index=idx,
        )
        db.session.add(stop)
        db.session.flush()  # need stop.id

        # TripActivities
        for act_id in activity_ids:
            db.session.add(TripActivity(
                trip_stop_id=stop.id,
                activity_id=act_id,
                scheduled_date=start_date,
            ))

        # Per-stop budget
        if budget_val is not None:
            total_budget += budget_val
            db.session.add(Budget(
                trip_id=trip_id,
                category=f"stop_{stop.id}",
                estimated_cost=budget_val,
                actual_cost=None,
            ))



    # Update trip overall dates from the first/last stops
    all_starts = [_parse_date(s.get("start_date","")) for s in sections]
    all_ends   = [_parse_date(s.get("end_date",""))   for s in sections]
    valid_starts = [d for d in all_starts if d]
    valid_ends   = [d for d in all_ends   if d]
    if valid_starts:
        trip.start_date = min(valid_starts)
    if valid_ends:
        trip.end_date = max(valid_ends)

    db.session.commit()

    return jsonify({
        "ok": True,
        "stop_count": len(sections),
        "redirect": url_for("itinerary.view", trip_id=trip_id),
    })


# ---------------------------------------------------------------------------
# AJAX: activities for a city (same as trips_bp version, kept here too)
# ---------------------------------------------------------------------------

@itinerary_bp.route("/trips/api/city-activities/<int:city_id>")
@login_required
def city_activities(city_id: int):
    from app.routes.trips import _seed_activities_for_city
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


# ---------------------------------------------------------------------------
# Read-only Itinerary Summary View
# ---------------------------------------------------------------------------

@itinerary_bp.route("/trips/<int:trip_id>/itinerary/view")
@login_required
def summary(trip_id: int):
    trip = _get_own_trip(trip_id)
    stops = trip.stops.order_by(TripStop.order_index).all()
    
    # Process stops to compute days and attach activities
    # To keep "Day N" relative to the trip, we track offset from trip.start_date
    processed_stops = []
    
    for stop in stops:
        days = []
        if stop.start_date and stop.end_date and trip.start_date:
            current_date = stop.start_date
            while current_date <= stop.end_date:
                day_num = (current_date - trip.start_date).days + 1
                # Find activities for this specific day
                activities_on_day = TripActivity.query.filter_by(
                    trip_stop_id=stop.id,
                    scheduled_date=current_date
                ).join(Activity).all()
                
                days.append({
                    "date": current_date,
                    "day_num": day_num,
                    "activities": activities_on_day
                })
                from datetime import timedelta
                current_date += timedelta(days=1)
        elif not stop.start_date and not stop.end_date:
             # Stop with no dates, unscheduled
             # We just attach all activities it has
             activities = TripActivity.query.filter_by(trip_stop_id=stop.id).join(Activity).all()
             days.append({
                 "date": None,
                 "day_num": None,
                 "activities": activities
             })
             
        stop.computed_days = days
        processed_stops.append(stop)

    # Calculate budget logic
    # Sum all Budget rows for this trip (excluding legacy desc_ rows with null costs just in case)
    budgets = Budget.query.filter(
        Budget.trip_id == trip.id,
        Budget.estimated_cost.isnot(None)
    ).all()
    
    total_budget = sum(b.estimated_cost or 0 for b in budgets)
    
    # Break down by category
    budget_by_category = {}
    for b in budgets:
        # If category starts with stop_, resolve it to the city name
        cat_name = b.category
        if b.category.startswith("stop_"):
            stop_id_str = b.category.split("_")[1]
            try:
                stop_ref = TripStop.query.get(int(stop_id_str))
                if stop_ref:
                    cat_name = f"{stop_ref.city.name} stop"
            except:
                pass
                
        budget_by_category[cat_name] = budget_by_category.get(cat_name, 0) + (b.estimated_cost or 0)

    # Sort categories by value
    sorted_budget_categories = sorted(budget_by_category.items(), key=lambda x: x[1], reverse=True)

    return render_template(
        "summary.html",
        trip=trip,
        stops=processed_stops,
        total_budget=total_budget,
        budget_by_category=sorted_budget_categories,
        TYPE_ICONS=TYPE_ICONS
    )
