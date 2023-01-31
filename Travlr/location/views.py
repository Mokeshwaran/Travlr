import datetime
import os
import uuid
from math import sqrt

import polyline
from flask import Blueprint, jsonify, request, Response
from googleplaces import GooglePlaces
from sqlalchemy.orm import aliased

from Travlr import db, app
from Travlr.constants import constants
from Travlr.exceptions.data_not_found_exception import DataNotFoundException
from Travlr.location.model import Location
from Travlr.travel.model import Travel
from Travlr.travel.views import get_directions

views = Blueprint('views', __name__)
timestamp = datetime.datetime
google_places = GooglePlaces(os.getenv('API_KEY'))


@views.route('/view/<travel_id>', methods = [constants.GET])
def view_locations(travel_id: int) -> Response:
    """
    This method will retrieve the location details from the database
    :return: location details
    :raise DataNotFoundException: if the data is not found
    """
    travel_table = aliased(Travel)
    location_table = aliased(Location)
    with app.app_context():
        query = location_table.query.join(travel_table, travel_table.id == travel_id).all()
        print(query)
        if not query:
            app.logger.warning("Location data is not available")
            raise DataNotFoundException("Location data is not available", 404)
        else:
            app.logger.info("Fetching location data")
            return jsonify(query)


@views.route('/add/<travel_id>', methods = [constants.POST])
def add_location(travel_id: int) -> Response:
    """
    This method is used to add location details to the database
    :param travel_id: id of the travel
    :return: JSON response of the travel
    """
    location_type = request.args.get('location')
    with app.app_context():
        travel = db.session.query(Travel).filter_by(id=travel_id).first()
        if travel is not None:
            directions = get_directions(travel.origin_name, travel.destination_name)
            get_locations(directions, location_type, travel)
        else:
            db.session.rollback()
            app.logger.warning("Travel data not found to add location")
            raise DataNotFoundException("Travel data not found to add location",
                                        constants.CODE_404)
    return jsonify({
        constants.ID: str(uuid.uuid1()),
        constants.DESCRIPTION: "Location added successfully",
        constants.STATUS_CODE: constants.CODE_200
    })

def insert_location(location_name: str, location_type: str, lat: float, lng: float,
                    travel: Travel) -> str:
    """
    This method will add location data to the database for faster loading
    of map data
    :param travel: Travel object
    :param location_name: name of the location
    :param location_type: type of location (e.g: Cafe, Restaurant, etc.)
    :param lat: latitude of the location
    :param lng: longitude of the location
    """
    created_date = timestamp.now()
    with app.app_context():
        query = db.session.query(Location).filter(Location.location_name == location_name,
                                                  Location.location_type == location_type)
        if query.first() is None:
            app.logger.info("Adding location details")
            travel_data = Travel.query.filter_by(id=travel.id).first()
            travel_data.location_travel.append(Location(location_name=location_name,
                                                        lat=lat, lng=lng,
                                                        location_type=location_type,
                                                        created_date=created_date))
            db.session.add(travel_data)
            db.session.commit()
            app.logger.info("Added location details")
        else:
            app.logger.info("Updating location data")
            query.update({
                constants.LOCATION_NAME : location_name,
                constants.LOCATION_TYPE : location_type,
                constants.UPDATED_DATE: timestamp.now()
            }, synchronize_session=constants.FETCH)
            db.session.commit()
            app.logger.info("Updated location data")
    app.logger.info(f"Added location details of location: {location_name}")
    return "Location added successfully"


def get_locations(directions: dict, location_type: str, travel: Travel) -> dict:
    """
    This method will get the location details from the travel and
    stores it in database for faster loading of map data.
    :param travel: Travel object
    :param directions: directions JSON response obtained from Google Maps API.
    :param location_type: type of the location (e.g: Cafe, Restaurant, etc.)
    :return: JSON response of locations
    :raise DataNotFoundException: if the data is not found
    """
    latlng = polyline.decode(directions['routes'][0]['overview_polyline']['points'])
    location_dict = {}
    with app.app_context():
        query = db.session.query(Location).filter_by(location_type=location_type).all()
        increment = 0
        if query:
            for location in query:
                if increment > len(latlng):
                    break
                distance = sqrt((latlng[increment][0] - location.lat)**2 +
                                (latlng[increment][1] - location.lng)**2)
                if distance <= constants.PRECISION_RADIUS:
                    location_dict[location.location_name] = (location.lat, location.lng)
                    increment += constants.INCREMENT
                else:
                    while increment < len(latlng):
                        location = get_nearby_location(latlng, increment, location_type,
                                                       travel)
                        if location is not None:
                            location_dict[location[0]] = (location[1], location[2])
                        increment += constants.INCREMENT
        else:
            while increment < len(latlng):
                get_nearby_location(latlng, increment, location_type, travel)
                increment += constants.INCREMENT
    return location_dict


def get_nearby_location(latlng: list[tuple], increment: int, location_type: str,
                        travel: Travel) -> tuple[str, float, float]:
    """
    This method will be executed if location data is not found in the database.
    :param travel: Travel object
    :param latlng: list of tuple of latitude and longitude
    :param increment: integer value of incrementation
    :param location_type: type of location (e.g: Restaurant, Cafe, etc.)
    """
    nearby_place = google_places.nearby_search(
        lat_lng={constants.LAT: latlng[increment][0],
                 constants.LNG: latlng[increment][1]},
        radius=constants.RADIUS,
        type=location_type
    ).raw_response

    # filtering some responses that might be empty and give ZERO_RESULTS
    if nearby_place['status'] != constants.ZERO_RESULTS and\
        nearby_place['results'][0]['business_status'] == constants.OPERATIONAL:
        location_name = nearby_place['results'][0]['name']
        lat = nearby_place['results'][0]['geometry']['location']['lat']
        lng = nearby_place['results'][0]['geometry']['location']['lng']
        app.logger.info("Location found")

        # adding location data to the database obtained from the Google Maps API
        insert_location(location_name, location_type, lat, lng, travel)
        app.logger.info("Location Added")
        return location_name, lat, lng