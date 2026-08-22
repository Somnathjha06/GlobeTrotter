from app import db


class Budget(db.Model):
    """A budget line-item for a Trip, grouped by category."""

    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False)   # e.g. "flights", "hotels", "food"
    estimated_cost = db.Column(db.Float, nullable=True)
    actual_cost = db.Column(db.Float, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Budget id={self.id} trip_id={self.trip_id} "
            f"category={self.category!r} estimated={self.estimated_cost}>"
        )
