from flask import Blueprint, request, jsonify

from Travlr.vehicle.model import Vehicle

views = Blueprint('views', __name__)
vehicle = Vehicle()

@views.route('/view', methods = ['GET'])
def view_vehicles():
    return vehicle.get()

@views.route('/add', methods = ['POST'])
def add_vehicle():
    data = request.json
    user_id = data['user_id']
    vehicle_type = data['vehicle_type']
    model_name = data['model_name']
    mileage = data['mileage']
    fuel_type = data['fuel_type']

    return jsonify(vehicle.post(user_id=user_id, vehicle_type=vehicle_type, model_name=model_name,
                        mileage=mileage, fuel_type=fuel_type))

@views.route('/delete', methods = ['DELETE'])
def delete():
    vehicle_id = request.json['vehicle_id']
    return vehicle.delete(vehicle_id)

@views.route('/update/<vehicle_id>', methods = ['PATCH'])
def update(vehicle_id):
    data = request.json
    vehicle_data = vehicle.get_vehicle(vehicle_id)
    vehicle_type = data.get('vehicle_type')
    model_name = data.get('model_name')
    mileage = data.get('mileage')
    fuel_type = data.get('fuel_type')
    if vehicle_data is not None:
        return vehicle.update(vehicle_data['vehicle_id'], vehicle_type, model_name, mileage, fuel_type)
