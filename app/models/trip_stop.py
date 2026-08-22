from app import db


class TripStop(db.Model):
    """An ordered city stop within a Trip."""

    __tablename__ = "trip_stops"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False, index=True)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, nullable=False, default=0)

    # Relationships
    trip_activities = db.relationship(
        "TripActivity",
        backref="trip_stop",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<TripStop id={self.id} trip_id={self.trip_id} "
            f"city_id={self.city_id} order={self.order_index}>"
        )
