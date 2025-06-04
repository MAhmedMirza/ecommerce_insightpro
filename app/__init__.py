from flask import Flask
from .config import Config
import logging
from sqlalchemy import text
from .extensions import db, login_manager, mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import models after db initialization
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Test database connection
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logging.info("Database connection successful!")
        except Exception as e:
            logging.error(f"Database connection failed: {str(e)}")
            raise RuntimeError("Could not establish database connection") from e

    # Initialize Celery
    from .tasks.celery_utils import make_celery
    celery = make_celery(app)
    app.extensions["celery"] = celery

    # Initialize ETL task
    from .tasks import create_task
    from .tasks import run_etl_process as task_var
    global task_var
    task_var = create_task(celery)

    # Register blueprints
    from .routes import main_bp
    from .auth import auth_blueprint
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_blueprint)

    return app