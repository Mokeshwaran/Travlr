import datetime
import json

from flask import Blueprint, request, jsonify

from Travlr import db, app
from Travlr.constants import constants
from Travlr.exceptions.data_not_found_exception import DataNotFoundException
from Travlr.vehicle.model import Vehicle

views = Blueprint('views', __name__)
timestamp = datetime.datetime


@views.route('/view/<user_id>', methods = [constants.GET])
def view_vehicles(user_id):
    """
    This method will retrieve all vehicle details associated
    with the user from the database
    :param user_id: id of the user who created the vehicle
    :return: all vehicle details
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        query = db.session.query(Vehicle).filter_by(id=user_id).all()
        if query is None:
            app.logger.warning("Vehicle data is not available")
            raise DataNotFoundException("Vehicle data is not available",
                                        constants.CODE_404)
        else:
            app.logger.info("Fetching vehicle data")
            return json.dumps(query)


@views.route('/view-one/<vehicle_id>', methods = [constants.GET])
def view_vehicle(vehicle_id):
    """
    This method will retrieve single vehicle detail from the database.
    :return: Single vehicle data as JSON response
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        query = db.session.query(Vehicle).filter_by(id=vehicle_id, is_deleted=0).first()
        if query is None:
            app.logger.warning("Vehicle data is not available")
            raise DataNotFoundException("Vehicle data is not available",
                                        constants.CODE_404)
        else:
            app.logger.info("Fetching vehicle data")
            return json.dumps(query)


@views.route('/add', methods = [constants.POST])
def add_vehicle():
    """
    This method will add a single vehicle data to the database
    :return: added vehicle detail
    """
    data = request.json
    user_id = data['user_id']
    travel_id = data['travel_id']
    vehicle_type = data['vehicle_type']
    model_name = data['model_name']
    mileage = data['mileage']
    fuel_type = data['fuel_type']
    is_deleted = 0
    created_date = timestamp.now()
    created_by = user_id
    app.logger.info("Adding vehicle details")
    with app.app_context():
        db.session.add(Vehicle(user_id=user_id, travel_id=travel_id, vehicle_type=vehicle_type,
                               model_name=model_name, mileage=mileage,
                               fuel_type=fuel_type, is_deleted=is_deleted,
                               created_date=created_date, created_by=created_by))
        db.session.commit()
    app.logger.info("Added vehicle details")
    return "added"


@views.route('/delete/<vehicle_id>', methods = [constants.DELETE])
def delete_vehicle(vehicle_id):
    """
    This method will delete a vehicle from the database
    :return: deleted vehicle detail
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        vehicle = db.session.query(Vehicle).filter_by(id=vehicle_id).first()
        if vehicle is None:
            app.logger.warn(f"No travel found - vehicle_id: {vehicle_id}")
            raise DataNotFoundException("vehicle data not found", constants.CODE_404)
        vehicle.is_deleted = 1
        vehicle.updated_date = str(timestamp.now())
        vehicle.updated_by = vehicle_id
        db.session.commit()
        app.logger.info(f"Vehicle deleted successfully - Vehicle_id: {vehicle.id}")
        return ({
            constants.ID: vehicle.id,
            constants.STATUS_CODE: constants.CODE_200,
            constants.DESCRIPTION: 'Vehicle Deleted Successfully',
            constants.TIMESTAMP: str(timestamp.now())
        })


@views.route('/update/<user_id>/<vehicle_id>', methods = [constants.PATCH])
def update_vehicle(user_id, vehicle_id):
    """
    This method will update a vehicle based on the vehicle_id and user_id
    :param user_id: id of the user
    :param vehicle_id: id of the vehicle
    :return: updated vehicle detail
    :raise DataNotFoundException: if the data is not found
    """
    data = request.json
    vehicle_type = data.get('vehicle_type')
    model_name = data.get('model_name')
    mileage = data.get('mileage')
    fuel_type = data.get('fuel_type')

    with app.app_context():
        vehicle = db.session.query(Vehicle).filter_by(id=vehicle_id, user_id=user_id).first()
        app.logger.info(f"Updating vehicle details - vehicle_id: {vehicle_id}")
        if vehicle_type is not None:
            vehicle.vehicle_type = vehicle_type
            app.logger.info("Updated vehicle_type")
        if model_name is not None:
            vehicle.model_name = model_name
            app.logger.info("Updated model_name")
        if mileage is not None:
            vehicle.mileage = mileage
            app.logger.info("Updated mileage")
        if fuel_type is not None:
            vehicle.fuel_type = fuel_type
            app.logger.info("Updated fuel_type")
        if vehicle is not None:
            vehicle.updated_date = timestamp.now()
            app.logger.info("Updated updated_date")
            vehicle.updated_user = user_id
            app.logger.info("Updated updated_user")
            db.session.commit()
            app.logger.info("Updated vehicle")
        else:
            app.logger.warning("Vehicle data not found")
            raise DataNotFoundException("Vehicle data not found", constants.CODE_404)
    return json.dumps(vehicle)
