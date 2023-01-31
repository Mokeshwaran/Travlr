from dataclasses import dataclass

from flask_serialize import FlaskSerialize

from Travlr import db

fs_mixin = FlaskSerialize(db)
user_travel = db.Table('user_travel',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('travel_id', db.Integer, db.ForeignKey('travel.id')),
                       db.PrimaryKeyConstraint('user_id', 'travel_id')
                       )


@dataclass(kw_only=True)
class User(db.Model, fs_mixin):
    id: int
    name: str
    email: str
    mobile_number: str
    gender: str
    travels: user_travel

    """
    This class is a model class for User
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    mobile_number = db.Column(db.String(255), unique=True)
    gender = db.Column(db.String(255))
    is_deleted = db.Column(db.Boolean)
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    created_by = db.Column(db.String(255))
    updated_by = db.Column(db.String(255))
    expense = db.relationship('Expense', backref='user')
    vehicle = db.relationship('Vehicle', backref='user')
    # travels = db.relationship('Travel', secondary=user_travel, backref="users")

    def __init__(self, user_id=None, name=None, email=None, password=None,
                 date_of_birth=None, mobile_number=None, gender=None, is_deleted=0,
                 created_date=None, updated_date=None, created_user=None,
                 updated_user=None):
        self.id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.date_of_birth = date_of_birth
        self.mobile_number = mobile_number
        self.gender = gender
        self.is_deleted = is_deleted
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_user = created_user
        self.updated_user = updated_user
