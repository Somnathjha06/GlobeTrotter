from app import db


class Activity(db.Model):
    """A bookable / schedulable activity available in a City."""

    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(100), nullable=True)       # e.g. "sightseeing", "food", "adventure"
    cost = db.Column(db.Float, nullable=True)             # estimated cost in USD
    duration = db.Column(db.Float, nullable=True)         # hours

    # Relationships
    trip_activities = db.relationship(
        "TripActivity",
        backref="activity",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Activity id={self.id} name={self.name!r} city_id={self.city_id}>"
