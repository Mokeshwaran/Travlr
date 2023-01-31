import datetime
import json
import os
import urllib
import polyline

from flask import Blueprint, request, jsonify, Response

from Travlr import db, app
from Travlr.constants import constants
from Travlr.exceptions.data_not_found_exception import DataNotFoundException
from Travlr.expense.model import Expense
from Travlr.fuel.model import Fuel
from Travlr.travel.views import get_directions
from Travlr.travel.model import Travel
from Travlr.vehicle.model import Vehicle

views = Blueprint('views', __name__)
timestamp = datetime.datetime


@views.route('/view/<user_id>', methods = [constants.GET])
def view_expenses(user_id: int) -> Response:
    """
    This method is used to get the expense associated with the given user_id
    :param user_id: id of the user
    :return: JSON response of expense
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        query = db.session.query(Expense).filter_by(user_id=user_id, is_deleted=0).all()
        if not query:
            app.logger.warning("Expense data is not available")
            raise DataNotFoundException("Expense data is not available", 404)
        else:
            app.logger.info("Fetching expense data")
            return jsonify(query)

@views.route('/view-one/<user_id>/<travel_id>', methods = [constants.GET])
def view_expense(user_id: int, travel_id: int) -> Response:
    """
    This method is used to get the expense associated
    with the given user_id and travel_id
    :param user_id: id of the user
    :param travel_id: id of the travel
    :return: JSON response of the expense
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        query = db.session.query(Expense).filter_by(user_id=user_id,
                                                    travel_id=travel_id,
                                                    is_deleted=0).all()
        if query is None:
            app.logger.warning("Expense data is not available")
            raise DataNotFoundException("Expense data is not available",
                                        constants.CODE_404)
        else:
            app.logger.info("Fetching expense data")
            return jsonify(query)

@views.route('/add/<user_id>/<travel_id>', methods = [constants.POST])
def add_expense(travel_id: int, user_id: int) -> Response:
    """
    This method is used to add the expense data based on the travel_id
    :param user_id: id of the user
    :param travel_id: id of the travel
    :return: JSON response of the fuel_expense
    :raise DataNotFoundException: if the data is not found
    """
    data = request.json
    expense_type = data.get('expense_type')
    fare = data.get('fare')
    if travel_id is None:
        app.logger.warning("Travel id not found")
        raise DataNotFoundException("Travel id not found", constants.CODE_404)
    with app.app_context():
        app.logger.info("Getting vehicle and travel data")
        vehicles = db.session.query(Vehicle).filter_by(travel_id=travel_id).all()
        travel = db.session.query(Travel).filter_by(id=travel_id).first()
        fuel_expense = db.session.query(Expense).filter_by(travel_id=travel_id).first()

        if not vehicles and travel is None:
            app.logger.warning("Vehicle or Travel data not found")
            raise DataNotFoundException("Vehicle or Travel data not found", constants.CODE_404)

        if fuel_expense is None:
            fuel_expense = 0
            app.logger.info("Getting directions from Google Maps API")
            directions = get_directions(travel.origin_name, travel.destination_name)
            for vehicle in vehicles:
                app.logger.info("Calculating fuel expense")
                fuel_expense +=\
                    calculate_fuel_expense(vehicle.mileage, vehicle.fuel_type,
                                           directions)
            app.logger.info(f"Adding fuel expense")
            db.session.add(Expense(expense_type=constants.FUEL, fare=fuel_expense,
                                   user_id=user_id, travel_id=travel_id,
                                   created_date=str(timestamp.now()),
                                   created_by=user_id))

        if expense_type is not None and fare is not None:
            app.logger.info(f"Adding {expense_type} expense")
            db.session.add(Expense(expense_type=expense_type, fare=fare,
                               user_id=user_id, travel_id=travel_id,
                               created_date = str(timestamp.now()),
                               created_by = user_id))
        db.session.commit()
        app.logger.info("Added expense")
        return jsonify({
            constants.FUEL_EXPENSE: fuel_expense,
            constants.TYPE: expense_type,
            constants.FARE: fare
        })


@views.route('/delete/<user_id>/<travel_id>', methods = [constants.DELETE])
def delete_expense(user_id: int, travel_id: int) -> Response:
    """
    This method is used to delete an expense associated
    with the given user_id and travel_id
    :param user_id: id of the user
    :param travel_id: id of the travel
    :return: JSON response of the deleted data
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        expense = db.session.query(Expense).filter_by(travel_id=travel_id,
                                                      user_id=user_id,
                                                      is_deleted=0).first()
        if expense is None:
            app.logger.warn(f"No travel found - travel_id: {travel_id}")
            raise DataNotFoundException("Travel data not found", constants.CODE_404)
        expense.is_deleted = 1
        expense.updated_date = str(timestamp.now())
        expense.updated_by = user_id
        db.session.commit()
        app.logger.info(f"Expense deleted successfully - expense_id: {expense.id}")
        return jsonify({
            constants.ID: expense.id,
            constants.STATUS_CODE: constants.CODE_200,
            constants.DESCRIPTION: 'Expense Deleted Successfully',
            constants.TIMESTAMP: str(timestamp.now())
        })


@views.route('/update/<user_id>/<travel_id>', methods = [constants.PATCH])
def update_expense(user_id: int, travel_id: int) -> Response:
    """
    This method will be used to update an expense based on user_id and expense_id
    :param user_id: id of the user
    :param travel_id: id of the travel
    :return: JSON response of updated expense
    :raise DataNotFoundException: if the data is not found
    """
    data = request.json
    expense_type = data.get('expense_type')
    fare = data.get('fare')

    with app.app_context():
        expense = db.session.query(Expense).filter_by(travel_id=travel_id,
                                                      user_id=user_id,
                                                      expense_type=expense_type,
                                                      is_deleted=0).first()
        app.logger.info(f"Updating expense details - travel_id: {travel_id}")
        if expense is None:
            app.logger.warning("Expense data not found")
            raise DataNotFoundException("Expense data not found", constants.CODE_404)
        if expense_type is not None:
            expense.expense_type = expense_type
            app.logger.info("Updated expense_type")
        if fare is not None:
            expense.fare = fare
            app.logger.info("Updated fare")
        expense.updated_date = str(timestamp.now())
        app.logger.info("Updated updated_date")
        expense.updated_user = user_id
        app.logger.info("Updated updated_user")
        db.session.commit()
        app.logger.info("Updated expense")
        return jsonify(expense)


def calculate_fuel_expense(mileage: int, fuel_type: str, directions: dict) -> int:
    """
    This method is used to calculate fuel expense from the data given
    :param fuel_type: type of fuel used in the vehicle
    :param mileage: mileage of the vehicle
    :param directions: JSON response of directions
    :return: fuel_expense of the travel
    """
    mileage *= 1000
    travel_distance = 0
    fuel_expense = 0
    for dis in directions['routes'][0]['legs'][0]['steps']:
        app.logger.info('Calculating distance')
        travel_distance += dis['distance']['value']
        if travel_distance > mileage:
            coord = polyline.decode(dis['polyline']['points'])
            inc = 2 if int(travel_distance / mileage) == 1\
                else int(travel_distance / mileage)
            app.logger.info('Getting coordinates')
            travel_distance -= mileage
            for i in range(inc, 1, -1):
                inc = int(len(coord) / i)
                url =\
                    f"{constants.GEOCODE_URL}{coord[inc][0]}," \
                    f"{coord[inc][1]}{constants.AMPERSAND_KEY}{os.getenv('API_KEY')}"
                response = json.loads(urllib.request.urlopen(url).read())
                district_name =\
                    response['results'][-3]['address_components'][0]['long_name']
                with app.app_context():
                    app.logger.info('Getting fuel prices')
                    district_name = constants.KANCHEEPURAM\
                        if district_name == constants.CHENGALPATTU else district_name
                    fuel = db.session.query(Fuel).filter_by(district_name=district_name,
                                                            fuel_type=fuel_type).first()
                    if fuel is not None:
                        print(fuel.fuel_price)
                        app.logger.info(district_name, ": ", fuel.fuel_price)
                        fuel_expense += fuel.fuel_price
    return fuel_expense
