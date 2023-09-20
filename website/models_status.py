# models_status.py
from . import db  # Import the db instance you created

class StatusTable(db.Model):
    __bind_key__= "dmls_status"
    __tablename__ = 'status_table' 

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)
    machine = db.Column(db.Integer)
    status = db.Column(db.Text)
    material = db.Column(db.Text)
    end_datetime = db.Column(db.Integer)
    time_remaining = db.Column(db.REAL)
    build_id = db.Column(db.Text)
    current_height = db.Column(db.REAL)
