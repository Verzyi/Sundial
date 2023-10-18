from flask import Blueprint, render_template, current_app
from flask_login import current_user, login_required
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_migrate import upgrade as alembic_upgrade  # Import the upgrade function from flask_migrate

migrate_bp = Blueprint('migrate', __name__)
migrate = Migrate()

# Initialize the Migrate extension with the Blueprint and SQLAlchemy db object
def init_app(app, db):
    migrate.init_app(app, db)

# Register the upgrade-db route with the migrate_bp Blueprint
@login_required
@migrate_bp.route('/upgrade-db')
def upgrade_db():
    # Run migrations
    with current_app.app_context():
        alembic_upgrade()  # Use the upgrade function from flask_migrate to apply migrations
    return 'Database upgraded successfully!'


@login_required
@migrate_bp.route('/upgrade-machine')
def upgrade_machine():
    from . import db
    from .models import Machines  # Import your Machines model

    # Data to be added to the Machines table
    machine_data = [
    {"MachineSerial": "Si1849", "LocationID": 1, "MachineName": "1849", "MachineAlias": "M1", "MachineType": "M280"},
    {"MachineSerial": "Si1848", "LocationID": 1, "MachineName": "1848", "MachineAlias": "M2", "MachineType": "M280"},
    {"MachineSerial": "Si1476", "LocationID": 1, "MachineName": "1476", "MachineAlias": "M3", "MachineType": "M280"},
    {"MachineSerial": "Si1991", "LocationID": 1, "MachineName": "1991", "MachineAlias": "M4", "MachineType": "M280"},
    {"MachineSerial": "Si2001", "LocationID": 1, "MachineName": "2001", "MachineAlias": "M5", "MachineType": "M280"},
    {"MachineSerial": "Si2006", "LocationID": 1, "MachineName": "2006", "MachineAlias": "M6", "MachineType": "M280"},
    {"MachineSerial": "Si1989", "LocationID": 1, "MachineName": "1989", "MachineAlias": "M7", "MachineType": "M280"},
    {"MachineSerial": "Si1160", "LocationID": 1, "MachineName": "1160", "MachineAlias": "M8", "MachineType": "M280"},
    {"MachineSerial": "Si1852", "LocationID": 1, "MachineName": "1852", "MachineAlias": "M9", "MachineType": "M280"},
    {"MachineSerial": "Si1810", "LocationID": 1, "MachineName": "1810", "MachineAlias": "M10", "MachineType": "M280"},
    {"MachineSerial": "Si1853", "LocationID": 1, "MachineName": "1853", "MachineAlias": "M11", "MachineType": "M280"},
    {"MachineSerial": "Si1351", "LocationID": 1, "MachineName": "1351", "MachineAlias": "M12", "MachineType": "M280"},
    {"MachineSerial": "Si2643", "LocationID": 1, "MachineName": "2643", "MachineAlias": "M13", "MachineType": "M290"},
    {"MachineSerial": "Si2642", "LocationID": 1, "MachineName": "2642", "MachineAlias": "M14", "MachineType": "M290"},
    {"MachineSerial": "Si1882", "LocationID": 1, "MachineName": "1882", "MachineAlias": "M15", "MachineType": "M290"},
    {"MachineSerial": "Si3607", "LocationID": 1, "MachineName": "3607", "MachineAlias": "M16", "MachineType": "M400-4"},
    {"MachineSerial": "Si2813", "LocationID": 1, "MachineName": "2813", "MachineAlias": "M17", "MachineType": "M400-1"},
    {"MachineSerial": "GA3", "LocationID": 1, "MachineName": "Velo", "MachineAlias": "V1", "MachineType": "Sapphire"}
    ]


    # Loop through the machine_data list and add each machine to the database session
    for data in machine_data:
        machine = Machines(
            MachineSerial=data["MachineSerial"],
            LocationID=data["LocationID"],
            MachineName=data["MachineName"],
            MachineAlias=data["MachineAlias"],
            MachineType=data["MachineType"]
        )
        db.session.add(machine)

    # Commit the changes to the database
    # db.session.commit() turn this off so that it will not save it some one else uses it 

    # Optional: Print a message to confirm the data has been added
    print("Machine data added to the database successfully.")
    return 'Database upgraded all machines successfully!'