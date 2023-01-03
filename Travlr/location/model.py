from sqlalchemy import func

from Travlr import db


class Location(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    location_id = db.Column(db.String(50), unique=True)
    lat = db.Column(db.Float(precision=53))
    lng = db.Column(db.Float(precision=53))
    location_type = db.Column(db.String(15))
    created_date = db.Column(db.DateTime(), server_default=func.now())
    updated_date = db.Column(db.DateTime())

    def __init__(self, location_id=None, lat=None, lng=None, location_type=None,
                 created_date=None, updated_date=None):
        self.__location_id = location_id
        self.__lat = lat
        self.__lng = lng
        self.__location_type = location_type
        self.__created_date = created_date
        self.__updated_date = updated_date

    def get_location_data(self):
        ...

