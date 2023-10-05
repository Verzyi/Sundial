# models_status.py
from . import db  # Import the db instance you created
from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config['SQLALCHEMY_BINDS'] = {
#     'dmls_status': 'sqlite:///path/to/dmls_status.db'
# }
# db = SQLAlchemy(app)
class StatusTable(db.Model):
    __bind_key__= "dmls_status"
    __tablename__ = 'status_table' 

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    timestamp = db.Column(db.Integer)
    machine = db.Column(db.Integer)
    status = db.Column(db.Text)
    material = db.Column(db.Text)
    end_datetime = db.Column(db.Integer)
    time_remaining = db.Column(db.REAL)
    build_id = db.Column(db.Text)
    current_height = db.Column(db.REAL)

    def __repr__(self):
        return f"<StatusTable(id={self.id}, machine={self.machine}, status={self.status}, ...)>"  # Include other columns for representation