import enum
from app import db


class TripStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"


class Trip(db.Model):
    """A travel trip belonging to a User."""

    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    cover_photo = db.Column(db.String(512), nullable=True)
    status = db.Column(
        db.Enum(TripStatus),
        nullable=False,
        default=TripStatus.UPCOMING,
    )

    # Relationships
    stops = db.relationship(
        "TripStop",
        backref="trip",
        lazy="dynamic",
        order_by="TripStop.order_index",
        cascade="all, delete-orphan",
    )
    budgets = db.relationship(
        "Budget",
        backref="trip",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Trip id={self.id} name={self.name!r} status={self.status}>"
