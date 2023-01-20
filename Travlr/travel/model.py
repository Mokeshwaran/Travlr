import datetime
from dataclasses import dataclass

from flask_serialize import FlaskSerialize
# from marshmallow import schema

from Travlr import db
from Travlr.location.model import location_travel
from Travlr.fuel.model import fuel_travel

fs_mixin = FlaskSerialize(db)
timestamp = datetime.datetime


@dataclass
class Travel(db.Model):
    """
    This class is a model class for Travel
    """
    id: int
    origin_name: str
    origin_lat: float
    origin_lng: float
    destination_name: str
    destination_lat: float
    destination_lng: float
    distance: float
    places_visiting: str
    is_deleted: int
    created_date: datetime
    updated_date: datetime
    created_by: int
    updated_by: int


    __tablename__ = 'travel'
    id = db.Column(db.Integer(), primary_key=True)
    origin_name = db.Column(db.String(50))
    origin_lat = db.Column(db.Float())
    origin_lng = db.Column(db.Float())
    destination_name = db.Column(db.String(50))
    destination_lat = db.Column(db.Float())
    destination_lng = db.Column(db.Float())
    distance = db.Column(db.Float())
    places_visiting = db.Column(db.String(100))
    is_deleted = db.Column(db.Boolean)
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    created_by = db.Column(db.String(50))
    updated_by = db.Column(db.String(50))
    expense = db.relationship('Expense', backref='travel')
    vehicle_id = db.relationship('Vehicle', backref='vehicle')
    location_travel = db.relationship('Location', secondary=location_travel)
    fuel_travel = db.relationship('Fuel', secondary=fuel_travel)

    def __init__(self, travel_id=None, origin_name=None, origin_lat=None,
                 origin_lng=None, destination_name=None, destination_lat=None,
                 destination_lng=None, distance=None, places_visiting=None,
                 is_deleted=0, travel_type=None, created_date=None, updated_date=None,
                 created_by=None, updated_by=None):
        self.travel_id = travel_id
        self.origin_name = origin_name
        self.origin_lat = origin_lat
        self.origin_lng = origin_lng
        self.destination_name = destination_name
        self.destination_lat = destination_lat
        self.destination_lng = destination_lng
        self.distance = distance
        self.places_visiting = places_visiting
        self.travel_type = travel_type
        self.is_deleted = is_deleted
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_by = created_by
        self.updated_by = updated_by
