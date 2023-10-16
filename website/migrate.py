from flask import Blueprint, current_app
from flask_migrate import Migrate
from flask_migrate import upgrade as alembic_upgrade  # Import the upgrade function from flask_migrate

migrate_bp = Blueprint('migrate', __name__)
migrate = Migrate()

# Initialize the Migrate extension with the Blueprint and SQLAlchemy db object
def init_app(app, db):
    migrate.init_app(app, db)

# Register the upgrade-db route with the migrate_bp Blueprint
@migrate_bp.route('/upgrade-db')
def upgrade_db():
    # Run migrations
    with current_app.app_context():
        alembic_upgrade()  # Use the upgrade function from flask_migrate to apply migrations
    return 'Database upgraded successfully!'