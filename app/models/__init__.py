# Models package — import every model here so Alembic can discover all tables.
# Extensions are imported first to avoid circular dependencies.
from app import db, login_manager  # noqa: F401

from app.models.user import User          # noqa: F401
from app.models.trip import Trip          # noqa: F401
from app.models.city import City          # noqa: F401
from app.models.trip_stop import TripStop # noqa: F401
from app.models.activity import Activity  # noqa: F401
from app.models.trip_activity import TripActivity  # noqa: F401
from app.models.budget import Budget      # noqa: F401


@login_manager.user_loader
def load_user(user_id: str) -> "User | None":
    return db.session.get(User, int(user_id))
