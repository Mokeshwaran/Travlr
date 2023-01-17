import datetime
from dataclasses import dataclass

from flask_serialize import FlaskSerialize

from Travlr import db

fuel_travel = db.Table('travel_fuel', db.Model.metadata,
    db.Column('fuel_id', db.Integer, db.ForeignKey('fuel.id')),
    db.Column('travel_id', db.Integer, db.ForeignKey('travel.id'))
)

@dataclass
class Fuel(db.Model):
    """
    This class is a model class for Fuel
    """
    id: int
    district_name: str
    fuel_type: str
    fuel_price: float
    created_date: datetime
    updated_date: datetime
    created_by: datetime
    updated_by: datetime

    __tablename__ = 'fuel'
    id = db.Column(db.Integer(), primary_key=True)
    district_name = db.Column(db.String(50))
    fuel_type = db.Column(db.String(50))
    fuel_price = db.Column(db.Float())
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    created_by = db.Column(db.String(50))
    updated_by = db.Column(db.String(50))

    def __init__(self, district_name=None, fuel_type=None, fuel_price=None,
                 created_date=None, updated_date=None, created_by=None, updated_by=None):
        self.district_name = district_name
        self.fuel_type = fuel_type
        self.fuel_price = fuel_price
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_by = created_by
        self.updated_by = updated_by
