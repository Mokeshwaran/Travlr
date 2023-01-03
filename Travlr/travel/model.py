import datetime
import uuid

from flask import jsonify
from flask_restful import Resource
from Travlr import db

timestamp = datetime.datetime

class Travel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    travel_id = db.Column(db.String(50), unique=True)
    origin_lat = db.Column(db.Float(precision=53))
    origin_lng = db.Column(db.Float(precision=53))
    destination_lat = db.Column(db.Float(precision=53))
    destination_lng = db.Column(db.Float(precision=53))
    places_visiting = db.Column(db.String(100))
    buddies = db.Column(db.String(100))
    vehicle = db.Column(db.String(100))
    fuel_fare = db.Column(db.Integer())
    hotel_fare = db.Column(db.Integer())
    restaurant_fare = db.Column(db.Integer())
    toll_fare = db.Column(db.Integer())
    miscellaneous_fare = db.Column(db.Integer())
    total_fare = db.Column(db.Integer())
    is_deleted = db.Column(db.Boolean)
    created_date = db.Column(db.Date)
    updated_date = db.Column(db.Date)
    created_user = db.Column(db.String(50))
    updated_user = db.Column(db.String(50))

    travel_details = {}
    travel = {}
    def __init__(self, travel_id=None, origin_lat=None, origin_lng=None,
                 destination_lat=None, destination_lng=None, places_visiting=None,
                 buddies=None, vehicle=None, fuel_fare=None, hotel_fare=None,
                 restaurant_fare=None, toll_fare=None, miscellaneous_fare=None,
                 total_fare=None, share=None, is_deleted=0, travel_type=None,
                 created_date=None, updated_date=None, created_user=None,
                 updated_user=None):
        self.__travel_id = travel_id
        self.__origin_lat = origin_lat
        self.__origin_lng = origin_lng
        self.__destination_lat = destination_lat
        self.__destination_lng = destination_lng
        self.__places_visiting = places_visiting
        self.__buddies = buddies
        self.__vehicle = vehicle
        self.__fuel_fare = fuel_fare
        self.__hotel_fare = hotel_fare
        self.__restaurant_fare = restaurant_fare
        self.__toll_fare = toll_fare
        self.__miscellaneous_fare = miscellaneous_fare
        self.__total_fare = total_fare
        self.__share = share
        self.__travel_type = travel_type
        self.__is_deleted = is_deleted
        self.__created_date = created_date
        self.__updated_date = updated_date
        self.__created_user = created_user
        self.__updated_user = updated_user
        
    def post(self, origin_lat=None, origin_lng=None, destination_lat=None,
             destination_lng=None, places_visiting=None, buddies=None,
             vehicle=None, fuel_fare=None, hotel_fare=None, restaurant_fare=None,
             toll_fare=None, miscellaneous_fare=None, share=None, travel_type=None,
             updated_date=None, created_user=None, updated_user=None):
        self.travel_details["travel_id"] = str(uuid.uuid1())
        self.travel_details["origin_lat"] = origin_lat
        self.travel_details["origin_lng"] = origin_lng
        self.travel_details["destination_lat"] = destination_lat
        self.travel_details["destination_lng"] = destination_lng
        self.travel_details["places_visiting"] = places_visiting
        self.travel_details["buddies"] = buddies
        self.travel_details["vehicle"] = vehicle
        self.travel_details["fuel_fare"] = fuel_fare
        self.travel_details["hotel_fare"] = hotel_fare
        self.travel_details["restaurant_fare"] = restaurant_fare
        self.travel_details["toll_fare"] = toll_fare
        self.travel_details["miscellaneous_fare"] = miscellaneous_fare
        self.travel_details["total_fare"] = fuel_fare + hotel_fare + restaurant_fare\
                                            + toll_fare + miscellaneous_fare
        self.travel_details["share"] = share
        self.travel_details["is_deleted"] = 0
        self.travel_details["travel_type"] = travel_type
        self.travel_details["created_date"] = timestamp.now()
        self.travel_details["updated_date"] = updated_date
        self.travel_details["created_user"] = created_user
        self.travel_details["updated_user"] = updated_user
        self.travel[self.travel_details["travel_id"]] = self.travel_details.copy()
        return jsonify(self.travel)

    def get_locations(self, travel_id):
        ...


    def get(self):
        get_travel = {}
        for val in self.travel.values():
            if val['is_deleted'] != 1:
                get_travel[val['travel_id']] = val.copy()
        return get_travel

    def get_travel(self, travel_id):
        for key, val in self.travel.items():
            if travel_id in val.values() and val['is_deleted'] != 1:
                return val
        return jsonify({
            'status_code': 404,
            'description': 'User Not Found',
            'timestamp': str(timestamp.now())
        })

    def delete(self, travel_id):
        for key, val in self.travel.items():
            if key == travel_id and val['is_deleted'] != 1:
                val['is_deleted'] = 1
                return jsonify({
                    'id': val['travel_id'],
                    'status_code': 200,
                    'description': 'Travel Deleted Successfully',
                   'timestamp': str(timestamp.now())
                })
        return jsonify({
            'status_code': 404,
            'description': 'Travel Not Found',
            'timestamp': str(timestamp.now())
        })

    def update(self, travel_id=None, origin_lat=None, origin_lng=None,
               destination_lat=None, destination_lng=None, places_visiting=None,
               buddies=None, vehicle=None, fuel_fare=None, hotel_fare=None,
               restaurant_fare=None, toll_fare=None, miscellaneous_fare=None,
               share=None, travel_type=None):
        if origin_lat is not None:
            self.travel_details["origin_lat"] = origin_lat
        if origin_lng is not None:
            self.travel_details["origin_lng"] = origin_lng
        if destination_lat is not None:
            self.travel_details["destination_lat"] = destination_lat
        if destination_lng is not None:
            self.travel_details["destination_lng"] = destination_lng
        if places_visiting is not None:
            self.travel_details["places_visiting"] = places_visiting
        if buddies is not None:
            self.travel_details["buddies"] = buddies
        if vehicle is not None:
            self.travel_details["vehicle"] = vehicle
        if fuel_fare is not None:
            self.travel_details["fuel_fare"] = fuel_fare
        elif fuel_fare is None:
            fuel_fare = 0
        if hotel_fare is not None:
            self.travel_details["hotel_fare"] = hotel_fare
        elif hotel_fare is None:
            hotel_fare = 0
        if restaurant_fare is not None:
            self.travel_details["restaurant_fare"] = restaurant_fare
        elif restaurant_fare is None:
            restaurant_fare = 0
        if toll_fare is not None:
            self.travel_details["toll_fare"] = toll_fare
        elif toll_fare is None:
            toll_fare = 0
        if miscellaneous_fare is not None:
            self.travel_details["miscellaneous_fare"] = miscellaneous_fare
        elif miscellaneous_fare is None:
            miscellaneous_fare = 0
        if share is not None:
            self.travel_details["share"] = share
        if travel_type is not None:
            self.travel_details["travel_type"] = travel_type
        if travel_id is not None:
            self.travel_details['total_fare'] = fuel_fare + hotel_fare + restaurant_fare\
                                                + toll_fare + miscellaneous_fare
            self.travel_details['updated_date'] = timestamp.now()
            self.travel[travel_id] = self.travel_details.copy()
        return self.travel
        