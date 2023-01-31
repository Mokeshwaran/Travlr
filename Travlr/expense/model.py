from dataclasses import dataclass

from flask_serialize import FlaskSerialize

from Travlr import db
from Travlr.travel.model import Travel
from Travlr.user.model import User

fs_mixin = FlaskSerialize(db)

@dataclass(kw_only=True)
class Expense(db.Model, fs_mixin):
    """
    This class is a model class for Expense
    """
    id: int
    expense_type: float
    fare: float
    user: User.id
    travel: Travel.id

    __tablename__ = 'expense'
    id = db.Column(db.Integer(), primary_key=True)
    expense_type = db.Column(db.String(255))
    fare = db.Column(db.Integer())
    is_deleted = db.Column(db.Boolean)
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    created_by = db.Column(db.String(255))
    updated_by = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    travel_id = db.Column(db.Integer, db.ForeignKey('travel.id'))

    def __init__(self, user_id=None, travel_id=None, expense_type=None,
                 fare=None, is_deleted=False, created_date=None, updated_date=None,
                 created_by=None, updated_by=None):
        self.user_id = user_id
        self.travel_id = travel_id
        self.expense_type = expense_type
        self.fare = fare
        self.is_deleted = is_deleted
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_by = created_by
        self.updated_by = updated_by