from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import func



class PowderBlends(db.Model):
    PowderBlendPartID = db.Column(db.Integer, primary_key=True, nullable=False) 
    PowderBlendID = db.Column(db.Integer)
    OldPowderBlendID = db.Column(db.Integer)
    AddedWeight = db.Column(db.Float)
    DateAdded = db.Column(db.DateTime(timezone=True),default=func.now())
    PowderInventoryBatchID = db.Column(db.Integer)
  

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))



