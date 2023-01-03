import datetime
import uuid

from flask import jsonify
from Travlr import db
from flask_restful import Resource

timestamp = datetime.datetime


class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String(50))
    vehicle_id = db.Column(db.String(50), unique=True)
    vehicle_type = db.Column(db.String(20))
    model_name = db.Column(db.String(30))
    mileage = db.Column(db.Integer())
    fuel_type = db.Column(db.String(15))
    is_deleted = db.Column(db.Boolean)
    created_date = db.Column(db.Date)
    updated_date = db.Column(db.Date)
    created_user = db.Column(db.String(50))
    updated_user = db.Column(db.String(50))

    vehicle_details = {}
    vehicle = {}
    def __init__(self, user_id=None, vehicle_id=None, vehicle_type=None, model_name=None,
                 mileage=None, fuel_type=None, is_deleted=0, created_date=None,
                 updated_date=None, created_user=None, updated_user=None):
        self.__user_id = user_id
        self.__vehicle_id = vehicle_id
        self.__vehicle_type = vehicle_type
        self.__model_name = model_name
        self.__mileage = mileage
        self.__fuel_type = fuel_type
        self.__is_deleted = is_deleted
        self.__created_date = created_date
        self.__updated_date = updated_date
        self.__created_user = created_user
        self.__updated_user = updated_user

    def post(self, user_id=None, vehicle_type=None, model_name=None, mileage=None,
             fuel_type=None):
        # vehicle = Vehicle(user_id=user_id, vehicle_id=str(uuid.uuid1()), vehicle_type=vehicle_type,
        #                        model_name=model_name, mileage=mileage, fuel_type=fuel_type)
        # db.session.add(vehicle)
        # db.session.commit()
        self.vehicle_details['user_id'] = user_id
        self.vehicle_details['vehicle_id'] = str(uuid.uuid1())
        self.vehicle_details['vehicle_type'] = vehicle_type
        self.vehicle_details['model_name'] = model_name
        self.vehicle_details['mileage'] = mileage
        self.vehicle_details['fuel_type'] = fuel_type
        self.vehicle_details['is_deleted'] = 0
        self.vehicle_details['created_date'] = timestamp.now()
        self.vehicle_details['created_user'] = user_id
        self.vehicle[self.vehicle_details['vehicle_id']] = self.vehicle_details.copy()
        return self.vehicle

    def get(self):
        get_vehicle = {}
        for val in self.vehicle.values():
            if val['is_deleted'] != 1:
                get_vehicle[val['vehicle_id']] = val.copy()
        return get_vehicle

    def get_vehicle(self, vehicle_id):
        for key, val in self.vehicle.items():
            if vehicle_id in val.values() and val['is_deleted'] != 1:
                return val
        return jsonify({
            'status_code': 404,
            'description': 'Vehicle Not Found',
            'timestamp': str(timestamp.now())
        })

    def delete(self, vehicle_id):
        for key, val in self.vehicle.items():
            if key == vehicle_id and val['is_deleted'] != 1:
                val['is_deleted'] = 1
                return jsonify({
                    'id': val['vehicle_id'],
                    'status_code': 200,
                    'description': 'Vehicle Deleted Successfully',
                    'timestamp': str(timestamp.now())
                })
        return jsonify({
            'status_code': 404,
            'description': 'Vehicle Not Found',
            'timestamp': str(timestamp.now())
        })

    def update(self, vehicle_id=None, vehicle_type=None, model_name=None, mileage=None,
               fuel_type=None):
        if vehicle_type is not None:
            self.vehicle_details['vehicle_type'] = vehicle_type
        if model_name is not None:
            self.vehicle_details['model_name'] = model_name
        if mileage is not None:
            self.vehicle_details['mileage'] = mileage
        if fuel_type is not None:
            self.vehicle_details['fuel_type'] = fuel_type
        if vehicle_id is not None:
            self.vehicle_details['updated_date'] = timestamp.now()
            self.vehicle_details['updated_user'] = vehicle_id
            self.vehicle[vehicle_id] = self.vehicle_details.copy()
        return self.vehicle

