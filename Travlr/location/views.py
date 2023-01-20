import datetime
import os
from math import sqrt

import polyline
from flask import Blueprint, jsonify
from googleplaces import GooglePlaces

from Travlr import db, app
from Travlr.constants import constants
from Travlr.exceptions.data_not_found_exception import DataNotFoundException
from Travlr.location.model import Location
from Travlr.travel.model import Travel

views = Blueprint('views', __name__)
timestamp = datetime.datetime
google_places = GooglePlaces(os.getenv('API_KEY'))


@views.route('/view/<travel_id>', methods = [constants.GET])
def view_locations(travel_id):
    """
    This method will retrieve the location details from the database
    :return: location details
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        query = db.session.query(Location).filter_by(travel_id=travel_id).all()
        if query is None:
            app.logger.warning("Location data is not available")
            raise DataNotFoundException("Location data is not available", 404)
        else:
            app.logger.info("Fetching location data")
            return jsonify(query)


def add_location(location_name, location_type, lat, lng):
    """
    This method will add location data to the database for faster loading
    of map data
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
            travel = Travel.query.filter_by(id=travel_id)
            db.session.add(Location(location_name=location_name, lat=lat, lng=lng,
                                    location_type=location_type, created_date=created_date))
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
    return "Added successfully"


def get_locations(directions, location_type='restaurant'):
    """
    This method will get the location details from the travel and
    stores it in database for faster loading of map data.
    :param directions: directions JSON response obtained from Google Maps API.
    :param location_type: type of the location (e.g: Cafe, Restaurant, etc.)
    :return: JSON response of locations
    :raise DataNotFoundException: if the data is not found
    """
    latlng = polyline.decode(directions['routes'][0]['overview_polyline']['points'])
    location_dict = {}
    with app.app_context():
        query = db.session.query(Location).filter_by(location_type=location_type)
        locations = query.all()
        print(locations)
        inc = 0
        if locations != []:
            for location in locations:
                if inc > len(latlng):
                    break
                distance = sqrt((latlng[inc][0] - location.lat)**2 + (latlng[inc][1] - location.lng)**2)
                if distance <= constants.PRECISION_RADIUS:
                    location_dict[location.location_name] = (location.lat, location.lng)
                    inc += 30
                else:
                    get_nearby_location(latlng, inc, location_type)
                    inc += 30
        else:
            while inc < len(latlng):
                get_nearby_location(latlng, inc, location_type)
                inc += 30
    return location_dict


def get_nearby_location(latlng, inc, location_type='restaurant'):
    """
    This method will be executed if location data is not found in the database.
    :param latlng: list of tuple of latitude and longitude
    :param inc: integer value of incrementation
    :param location_type: type of location (e.g: Restaurant, Cafe, etc.)
    """
    nearby_place = google_places.nearby_search(
        lat_lng={constants.LAT: latlng[inc][0], constants.LNG: latlng[inc][1]},
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
        add_location(location_name, location_type, lat, lng)
        app.logger.info("Location Added")