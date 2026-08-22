from app import db


class City(db.Model):
    """A city that can be part of a trip itinerary."""

    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    country = db.Column(db.String(120), nullable=False)
    cost_index = db.Column(db.Float, nullable=True)       # relative cost index, e.g. 1.0 = average
    popularity = db.Column(db.Integer, nullable=True)     # rank / score

    # Relationships
    stops = db.relationship("TripStop", backref="city", lazy="dynamic")
    activities = db.relationship(
        "Activity",
        backref="city",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<City id={self.id} name={self.name!r} country={self.country!r}>"
