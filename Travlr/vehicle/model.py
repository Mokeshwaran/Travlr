import datetime
from dataclasses import dataclass

from flask_serialize import FlaskSerialize
from Travlr import db
# from Travlr.travel.model import Travel
from Travlr.user.model import User

timestamp = datetime.datetime
fs_mixin = FlaskSerialize(db)

@dataclass(kw_only=True)
class Vehicle(db.Model, fs_mixin):
    id: int
    vehicle_type : str
    model_name : str
    mileage : float
    fuel_type : str
    # user: int
    # travel: int

    """
    This class is a model class for Vehicle
    """
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer(), db.Sequence('id', start=1, increment=1),
                   primary_key=True)
    vehicle_type = db.Column(db.String(255))
    model_name = db.Column(db.String(255))
    mileage = db.Column(db.Integer())
    fuel_type = db.Column(db.String(255))
    is_deleted = db.Column(db.Boolean)
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    created_by = db.Column(db.String(255))
    updated_by = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    travel_id = db.Column(db.Integer, db.ForeignKey('travel.id'))

    def __init__(self, user_id=None, travel_id=None, vehicle_type=None, model_name=None,
                 mileage=None, fuel_type=None, is_deleted=0, created_date=None,
                 updated_date=None, created_by=None, updated_by=None):
        self.user_id = user_id
        self.travel_id = travel_id
        self.vehicle_type = vehicle_type
        self.model_name = model_name
        self.mileage = mileage
        self.fuel_type = fuel_type
        self.is_deleted = is_deleted
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_by = created_by
        self.updated_by = updated_by
