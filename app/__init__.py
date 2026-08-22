from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from config import config

# ---------------------------------------------------------------------------
# Extension instances (created here, initialised in create_app)
# ---------------------------------------------------------------------------
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app(config_name: str = "default") -> Flask:
    """Application factory."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(config[config_name])

    # ------------------------------------------------------------------
    # Initialise extensions
    # ------------------------------------------------------------------
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login_manager.init_app(flask_app)
    
    # Import models so the user_loader is registered and Alembic can detect tables
    import app.models  # noqa: F401

    # ------------------------------------------------------------------
    # Register blueprints
    # ------------------------------------------------------------------
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.trips import trips_bp
    from app.routes.itinerary import itinerary_bp
    from app.routes.budget import budget_bp
    from app.routes.search import search_bp

    flask_app.register_blueprint(auth_bp, url_prefix="/auth")
    flask_app.register_blueprint(main_bp)
    flask_app.register_blueprint(trips_bp, url_prefix="/trips")
    flask_app.register_blueprint(itinerary_bp)          # URLs start with /trips/<id>/itinerary
    flask_app.register_blueprint(budget_bp, url_prefix="/budget")
    flask_app.register_blueprint(search_bp)

    @flask_app.get("/")
    def home():
        # Authenticated users go straight to the dashboard
        if current_user.is_authenticated:
            return redirect(url_for("main.dashboard"))
        return render_template("home.html")

    return flask_app
