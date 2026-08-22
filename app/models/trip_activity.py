from app import db


class TripActivity(db.Model):
    """An Activity scheduled within a specific TripStop."""

    __tablename__ = "trip_activities"

    id = db.Column(db.Integer, primary_key=True)
    trip_stop_id = db.Column(
        db.Integer, db.ForeignKey("trip_stops.id"), nullable=False, index=True
    )
    activity_id = db.Column(
        db.Integer, db.ForeignKey("activities.id"), nullable=False, index=True
    )
    scheduled_date = db.Column(db.Date, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<TripActivity id={self.id} stop={self.trip_stop_id} "
            f"activity={self.activity_id} date={self.scheduled_date}>"
        )
