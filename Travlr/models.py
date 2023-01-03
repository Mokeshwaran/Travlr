class User:
    def __init__(self, id, updated_user=None, created_user=None, updated_date=None,
                 created_date=None, gender=None, mobile_number=None,
                 date_of_birth=None, password=None, email_id=None, name=None):
        self.id = id
        self.name = name
        self.email_id = email_id
        self.password = password
        self.date_of_birth = date_of_birth
        self.mobile_number = mobile_number
        self.gender = gender
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_user = created_user
        self.updated_user = updated_user


class Travel:
    def __init__(self, id=None, updated_user=None, created_user=None, updated_date=None,
                 created_date=None, travel_type=None, share=None, total_fare=None,
                 miscellaneous_fare=None, toll_fare=None, restaurant_fare=None,
                 hotel_fare=None, fuel_fare=None, vehicle=None, buddies=None,
                 places_visiting=None, destination_lng=None, destination_lat=None,
                 origin_lng=None, origin_lat=None):
        self.id = id
        self.origin_lat = origin_lat
        self.origin_lng = origin_lng
        self.destination_lat = destination_lat
        self.destination_lng = destination_lng
        self.places_visiting = places_visiting
        self.buddies = buddies
        self.vehicle = vehicle
        self.fuel_fare = fuel_fare
        self.hotel_fare = hotel_fare
        self.restaurant_fare = restaurant_fare
        self.toll_fare = toll_fare
        self.miscellaneous_fare = miscellaneous_fare
        self.total_fare = total_fare
        self.share = share
        self.travel_type = travel_type
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_user = created_user
        self.updated_user = updated_user



class Vehicle:
    def __init__(self, updated_user=None, created_user=None, updated_date=None,
                 created_date=None, fuel_type=None, mileage=None, model_name=None,
                 vehicle_type=None, user_id=None):
        self.user_id = user_id
        self.type = vehicle_type
        self.model_name = model_name
        self.mileage = mileage
        self.fuel_type = fuel_type
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_user = created_user
        self.updated_user = updated_user


class Fuel:
    def __init__(self, updated_date=None, created_date=None, fuel_price=None,
                 fuel_type=None, district_name=None, district_id=None):
        self.district_id = district_id
        self.district_name = district_name
        self.fuel_type = fuel_type
        self.fuel_price = fuel_price
        self.created_date = created_date
        self.updated_date = updated_date
