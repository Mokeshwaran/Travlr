from Travlr import db


class Fuel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    district_id = db.Column(db.String(50), unique=True)
    district_name = db.Column(db.String(50))
    fuel_type = db.Column(db.String(50))
    created_date = db.Column(db.Date)
    updated_date = db.Column(db.Date)
    created_user = db.Column(db.String(50))
    updated_user = db.Column(db.String(50))

    def __init__(self, district_id=None, district_name=None, fuel_type=None,
                 fuel_price=None, created_date=None, updated_date=None):
        self.__district_id = district_id
        self.__district_name = district_name
        self.__fuel_type = fuel_type
        self.__fuel_price = fuel_price
        self.__created_date = created_date
        self.__updated_date = updated_date

    # def add(self):

