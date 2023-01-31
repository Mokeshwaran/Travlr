import datetime
from dataclasses import dataclass

from flask_serialize import FlaskSerialize
from sqlalchemy import func
from Travlr import db

fs_mixin = FlaskSerialize(db)

location_travel = db.Table('travel_location', db.Model.metadata,
    db.Column('location_id', db.Integer, db.ForeignKey('location.id')),
    db.Column('travel_id', db.Integer, db.ForeignKey('travel.id'))
)


@dataclass
class Location(db.Model, fs_mixin):
    """
    This class is a model class for Location
    """
    id: int
    location_name: str
    lat: float
    lng: float
    location_type: str

    __tablename__ = 'location'
    id = db.Column(db.Integer(), primary_key=True)
    location_name = db.Column(db.String(255))
    lat = db.Column(db.Float())
    lng = db.Column(db.Float())
    location_type = db.Column(db.String(255))
    created_date = db.Column(db.DateTime(), server_default=func.now())
    updated_date = db.Column(db.DateTime())

    def __init__(self, location_name=None, lat=None, lng=None, location_type=None,
                 created_date=None, updated_date=None, created_by=None, updated_by=None):
        self.location_name = location_name
        self.lat = lat
        self.lng = lng
        self.location_type = location_type
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_by = created_by
        self.updated_by = updated_by
