import datetime
import json
import uuid

from flask import jsonify
from Travlr import db
from flask_restful import Resource
from flask_sqlalchemy import SQLAlchemy

timestamp = datetime.datetime


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    email_id = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    mobile_number = db.Column(db.String(10), unique=True)
    gender = db.Column(db.String(15))
    is_deleted = db.Column(db.Boolean)
    created_date = db.Column(db.Date)
    updated_date = db.Column(db.Date)
    created_user = db.Column(db.String(50))
    updated_user = db.Column(db.String(50))

    user_details = {}
    user = {}

    def __init__(self, user_id=None, name=None, email_id=None, password=None,
                 date_of_birth=None, mobile_number=None, gender=None, is_deleted=0,
                 created_date=None, updated_date=None, created_user=None,
                 updated_user=None):
        self.__id = user_id
        self.__name = name
        self.__email_id = email_id
        self.__password = password
        self.__date_of_birth = date_of_birth
        self.__mobile_number = mobile_number
        self.__gender = gender
        self.__is_deleted = is_deleted
        self.__created_date = created_date
        self.__updated_date = updated_date
        self.__created_user = created_user
        self.__updated_user = updated_user

    def post(self, name=None, email_id=None, password=None, date_of_birth=None,
             mobile_number=None, gender=None):
        self.user_details["user_id"] = str(uuid.uuid1())
        self.user_details["name"] = name
        self.user_details["email_id"] = email_id
        self.user_details["password"] = password
        self.user_details["date_of_birth"] = date_of_birth
        self.user_details["mobile_number"] = mobile_number
        self.user_details["gender"] = gender
        self.user_details["is_deleted"] = 0
        self.user[self.user_details["user_id"]] = self.user_details.copy()
        return self.user

    def get(self):
        get_user = {}
        for val in self.user.values():
            if val['is_deleted'] != 1:
                get_user[val['user_id']] = val.copy()
        return get_user

    def get_user(self, email_id):
        for key, val in self.user.items():
            if email_id in val.values() and val['is_deleted'] != 1:
                return json.dumps(val)
        return jsonify({
            'status_code': 404,
            'description': 'User Not Found',
            'timestamp': str(timestamp.now())
        })

    def delete(self, email_id):
        for key, val in self.user.items():
            if email_id in val.values() and val['is_deleted'] != 1:
                val['is_deleted'] = 1
                return jsonify({
                    'id': val['user_id'],
                    'status_code': 200,
                    'description': 'User Deleted Successfully',
                   'timestamp': str(timestamp.now())
                })
        return jsonify({
            'status_code': 404,
            'description': 'User Not Found',
            'timestamp': str(timestamp.now())
        })

    def update(self, user_id=None, name=None, password=None, date_of_birth=None,
               mobile_number=None, gender=None):
        if name is not None:
            self.user_details['name'] = name
        if password is not None:
            self.user_details['password'] = password
        if date_of_birth is not None:
            self.user_details['date_of_birth'] = date_of_birth
        if mobile_number is not None:
            self.user_details['mobile_number'] = mobile_number
        if gender is not None:
            self.user_details['gender'] = gender
        if user_id is not None:
            self.user[user_id] = self.user_details.copy()
        return self.user