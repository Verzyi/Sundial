# models_status.py

from . import db  # Import the db instance you created

class StatusTable(db.Model):
    __bind_key__= "dmls_status"
    __tablename__ = 'status_table'  # Match the actual table name in your dmls_status.db

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer, nullable=False)
    machine = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Text, nullable=False)
    material = db.Column(db.Text, nullable=False)
    end_datetime = db.Column(db.Integer, nullable=False)
    time_remaining = db.Column(db.REAL, nullable=False)
    build_id = db.Column(db.Text, nullable=False)
    current_height = db.Column(db.REAL, nullable=False)
