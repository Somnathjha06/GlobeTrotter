from flask import Blueprint, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from app import db
from app.models.city import City
from app.models.activity import Activity
from app.routes.trips import TYPE_ICONS, _seed_activities_for_city

search_bp = Blueprint("search", __name__, template_folder="../templates/search")

@search_bp.route("/search")
@login_required
def index():
    q = request.args.get("q", "").strip()
    type_filter = request.args.get("type", "all")
    sort_by = request.args.get("sort", "popularity")
    group_by = request.args.get("group", "none")

    cities = []
    activities = []

    if q:
        # Filter cities by name or country
        cities_query = City.query.filter(
            or_(
                City.name.ilike(f"%{q}%"),
                City.country.ilike(f"%{q}%")
            )
        )
        # Filter activities by name or type
        activities_query = Activity.query.filter(
            or_(
                Activity.name.ilike(f"%{q}%"),
                Activity.type.ilike(f"%{q}%")
            )
        )

        if type_filter == "cities":
            cities = cities_query.all()
        elif type_filter == "activities":
            activities = activities_query.all()
        else:
            cities = cities_query.all()
            activities = activities_query.all()
    else:
        # If no query, maybe show a default set of cities?
        if type_filter in ["all", "cities"]:
            cities = City.query.limit(10).all()
        if type_filter in ["all", "activities"]:
            # Let's seed activities if they don't exist
            all_cities = City.query.all()
            for c in all_cities:
                if c.activities.count() == 0:
                    _seed_activities_for_city(c)
            activities = Activity.query.limit(10).all()

    # Apply sorting
    if sort_by == "name":
        cities.sort(key=lambda c: c.name.lower())
        activities.sort(key=lambda a: a.name.lower())
    elif sort_by == "cost":
        # Cost is only for activities
        activities.sort(key=lambda a: a.cost or 0)
    elif sort_by == "popularity":
        # Placeholder for popularity sorting if there's no popularity field
        pass

    # Process activities to add icons
    for a in activities:
        a.icon = TYPE_ICONS.get(a.type, "📌")

    return render_template(
        "index.html",
        q=q,
        type_filter=type_filter,
        sort_by=sort_by,
        group_by=group_by,
        cities=cities,
        activities=activities
    )
