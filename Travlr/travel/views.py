import datetime
import json
import pickle
import urllib
import os
import uuid
from typing import Any

import googlemaps

from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, Response
from sqlalchemy.orm import aliased

from Travlr import app, db
from Travlr.constants import constants
from Travlr.exceptions.data_not_found_exception import DataNotFoundException
from Travlr.travel.model import Travel
from Travlr.user.model import User

load_dotenv()
map_client = googlemaps.Client(os.getenv('API_KEY'))
views = Blueprint('views', __name__)
timestamp = datetime.datetime

@views.route('/view/<user_id>', methods = [constants.GET])
def view_travels(user_id: int) -> Response:
    """
    This method will retrieve all the travels from the database.
    :param user_id: id of the user
    :return: All travel data as JSON response
    :raise DataNotFoundException: if the data is not found
    """
    # travel_table = aliased(Travel)
    # user_table = aliased(User)
    with app.app_context():
        query = Travel.query.filter_by(is_deleted=0, created_by=user_id).all()
        if not query:
            app.logger.warning("Travel data is not available")
            raise DataNotFoundException("Travel data is not available",
                                        constants.CODE_404)
        else:
            app.logger.info("Fetching travel data")
            return jsonify(query)


@views.route('/view-one/<travel_id>', methods = [constants.GET])
def view_travel(travel_id: int) -> Response:
    """
    This method will retrieve single travel detail from the database.
    :param travel_id: id of the travel
    :return: Single travel data as JSON response
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        query = db.session.query(Travel).filter_by(id=travel_id, is_deleted=0).first()
        if query is None:
            app.logger.warning("Travel data is not available")
            raise DataNotFoundException("Travel data is not available",
                                        constants.CODE_404)
        else:
            app.logger.info("Fetching travel data")
            return jsonify(query)


@views.route('/add', methods = [constants.POST])
def add_travel() -> Response:
    """
    This method will add a travel detail to the database based on the user request.
    :return: Travel detail as JSON response
    """
    data = request.json
    user_id = data['user_id']
    origin_name = data['origin_name']
    destination_name = data['destination_name']
    places_visiting = data.get('places_visiting')
    travel_type = data['travel_type']
    app.logger.info("Added travel data")

    # Calculating directions using Google Maps API
    directions = get_directions(origin_name, destination_name)

    # Getting latitude and longitude of origin and destination
    origin_lat = directions['routes'][0]['legs'][0]['start_location']['lat']
    origin_lng = directions['routes'][0]['legs'][0]['start_location']['lng']
    destination_lat = directions['routes'][0]['legs'][0]['end_location']['lat']
    destination_lng = directions['routes'][0]['legs'][0]['end_location']['lng']
    distance = directions['routes'][0]['legs'][0]['distance']['value']
    with app.app_context():
        user = User.query.filter_by(id=user_id, is_deleted=0).first()
        user.travels.append(Travel(origin_name=origin_name, origin_lat=origin_lat,
                                   origin_lng=origin_lng,
                                   destination_name=destination_name,
                                   destination_lat=destination_lat,
                                   destination_lng=destination_lng,
                                   places_visiting=places_visiting,
                                   distance=distance, travel_type=travel_type,
                                   created_date=timestamp.now(),
                                   created_by=user_id))
        db.session.add(user)
        db.session.commit()
    app.logger.info("Added travel details")
    return jsonify({
        constants.ID: str(uuid.uuid1()),
        constants.DESCRIPTION: "Travel added successfully",
        constants.STATUS_CODE: constants.CODE_200
    })


@views.route('/join/<user_id>/<travel_id>', methods = [constants.POST])
def join_travel(user_id: int, travel_id: int):
    with app.app_context():
        user = User.query.filter_by(id=user_id, is_deleted=0).first()
        travel = db.session.query(Travel).filter_by(id=travel_id, is_deleted=0).first()
        user.travels.append(travel)
        db.session.commit()
        return jsonify({
            constants.ID: str(uuid.uuid1()),
            constants.DESCRIPTION: "Joined travel successfully",
            constants.STATUS_CODE: constants.CODE_200
        })


@views.route('/delete/<travel_id>', methods = [constants.DELETE])
def delete_travel(travel_id: int) -> Response:
    """
    This method will delete a travel detail from the database.
    :param travel_id: id of the travel
    :return: Deleted travel detail
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        travel = db.session.query(Travel).filter_by(id=travel_id, is_deleted=0).first()
        if travel is not None:
            travel.is_deleted = 1
            db.session.commit()
            app.logger.info(f"Travel deleted successfully - travel_id: {travel.id}")
            return jsonify({
                constants.ID: travel.id,
                constants.STATUS_CODE: constants.CODE_200,
                constants.DESCRIPTION: 'Travel Deleted Successfully',
                constants.TIMESTAMP: str(timestamp.now())
            })
    app.logger.warn(f"No travel found - travel_id: {travel_id}")
    raise DataNotFoundException("Travel data not found", constants.CODE_404)


@views.route('/update/<travel_id>', methods = [constants.PATCH])
def update_travel(travel_id: int) -> Response:
    """
    This method will update a travel detail to the database.
    :param travel_id: id of the travel
    :return: Updated travel detail
    :raise DataNotFoundException: if the data is not found
    :raise MustNotBeEmptyException: if the given data in empty
    """
    data = request.json
    origin_name = data.get('origin_name')
    destination_name = data.get('destination_name')
    places_visiting = data.get('places_visiting')
    travel_type = data.get('travel_type')

    directions = get_directions(origin_name, destination_name)

    with app.app_context():
        travel = db.session.query(Travel).filter_by(id=travel_id, is_deleted=0).first()

        if origin_name is not None and destination_name is not None:
            travel.origin_name = origin_name
            travel.origin_lat = directions['routes'][0]['legs'][0]['start_location']['lat']
            travel.origin_lng = directions['routes'][0]['legs'][0]['start_location']['lng']
            app.logger.info("Updating origin_lat, origin_lng using directions API")
            travel.destination_name = destination_name
            travel.destination_lat = directions['routes'][0]['legs'][0]['end_location']['lat']
            travel.destination_lng = directions['routes'][0]['legs'][0]['end_location']['lng']
            app.logger.info("Updating destination_lat, destination_lng using directions API")
            travel.distance = directions['routes'][0]['legs'][0]['distance']['value']
        if places_visiting is not None:
            travel.places_visiting = places_visiting
        if travel_type is not None:
            travel.travel_type = travel_type
        if travel is not None:
            app.logger.info("Updating travel details")
            db.session.commit()
            app.logger.info("Updated travel details")
            return jsonify(travel)
        else:
            db.session.rollback()
            app.logger.warning("Travel data doesn't exist")
            raise DataNotFoundException("Travel data doesn't exist", constants.CODE_404)

def get_directions(origin_name: str, destination_name: str) -> Any:
    """
    This method is used to get the direction from the Google Maps API
    :param origin_name: Name of the origin
    :param destination_name: Name of the destination
    :return: JSON response of directions obtained from Google Maps API
    """
    request_url = constants.DIRECTIONS_URL + constants.ORIGIN_DESTINATION_KEY \
        .format(origin_name.replace(' ', '+'),
                destination_name.replace(' ', '+'),
                os.getenv('API_KEY'))
    app.logger.info("Fetching location data from Google Maps API")
    response = urllib.request.urlopen(request_url).read()
    directions = json.loads(response)
    return directions
