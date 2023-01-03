import json
import urllib

import googlemaps
import polyline
from dotenv import load_dotenv
from googleplaces import GooglePlaces
import os

load_dotenv()
map_client = googlemaps.Client(os.getenv('API_KEY'))
google_places = GooglePlaces(os.getenv('API_KEY'))

from flask import Blueprint, request, jsonify
from Travlr.travel.model import Travel

views = Blueprint('views', __name__)
travel = Travel()

@views.route('/view', methods = ['GET'])
def view_travels():
    return travel.get()

@views.route('/view-one', methods = ['GET'])
def view_travel():
    travel_id = request.json['travel_id']
    return jsonify(travel.get_travel(travel_id))

@views.route('/add', methods = ['POST'])
def add_travel():
    location_dict = {}
    data = request.json
    origin_name = data['origin_name']
    destination_name = data['destination_name']
    places_visiting = data['places_visiting']
    buddies = data['buddies']
    vehicle = data['vehicle']
    fuel_fare = data['fuel_fare']
    hotel_fare = data['hotel_fare']
    restaurant_fare = data['restaurant_fare']
    toll_fare = data['toll_fare']
    miscellaneous_fare = data['miscellaneous_fare']
    share = data['share']
    travel_type = data['travel_type']

    location = request.args.get('location')
    request_url = os.getenv('URL') + 'origin={}&destination={}&key={}'\
        .format(origin_name.replace(' ', '+'),
                destination_name.replace(' ', '+'),
                os.getenv('API_KEY'))
    response = urllib.request.urlopen(request_url).read()
    directions = json.loads(response)
    latlng = polyline.decode(directions['routes'][0]['overview_polyline']['points'])

    if location is not None:
        i = 0
        while i < len(latlng):
            loc = google_places.nearby_search(
                lat_lng={'lat': latlng[i][0], 'lng': latlng[i][1]},
                radius=200,
                type=location
            ).raw_response
            if loc['status'] != 'ZERO_RESULTS':
                location_dict[loc['results'][0]['name']] =\
                    (loc['results'][0]['geometry']['location']['lat'],
                     loc['results'][0]['geometry']['location']['lng'])
            i += 40

    origin_lat = directions['routes'][0]['legs'][0]['start_location']['lat']
    origin_lng = directions['routes'][0]['legs'][0]['start_location']['lng']
    destination_lat = directions['routes'][0]['legs'][0]['end_location']['lat']
    destination_lng = directions['routes'][0]['legs'][0]['end_location']['lng']
    travel.post(origin_lat=origin_lat, origin_lng=origin_lng,
                destination_lat=destination_lat, destination_lng=destination_lng,
                places_visiting=places_visiting, buddies=buddies, vehicle=vehicle,
                fuel_fare=fuel_fare, hotel_fare=hotel_fare,
                restaurant_fare=restaurant_fare, toll_fare=toll_fare,
                miscellaneous_fare=miscellaneous_fare, share=share,
                travel_type=travel_type)

    return location_dict

@views.route('/delete', methods = ['DELETE'])
def delete_travel():
    travel_id = request.json['travel_id']
    return travel.delete(travel_id)

@views.route('/update/<travel_id>', methods = ['PATCH'])
def update_travel(travel_id):
    data = request.json
    travel_data = travel.get_travel(travel_id)
    origin_name = data.get('origin_name')
    destination_name = data.get('destination_name')
    places_visiting = data.get('places_visiting')
    buddies = data.get('buddies')
    vehicle = data.get('vehicle')
    fuel_fare = data.get('fuel_fare')
    hotel_fare = data.get('hotel_fare')
    restaurant_fare = data.get('restaurant_fare')
    toll_fare = data.get('toll_fare')
    miscellaneous_fare = data.get('miscellaneous_fare')
    share = data.get('share')
    travel_type = data.get('travel_type')

    if origin_name is None:
        origin_lat = travel_data['origin_lat']
        origin_lng = travel_data['origin_lng']
    else:
        origin = map_client.geocode(origin_name)
        origin_lat = origin[0]['geometry']['location']['lat']
        origin_lng = origin[0]['geometry']['location']['lng']

    if destination_name is None:
        destination_lat = travel_data['destination_lat']
        destination_lng = travel_data['destination_lng']
    else:
        destination = map_client.geocode(destination_name)
        destination_lat = destination[0]['geometry']['location']['lat']
        destination_lng = destination[0]['geometry']['location']['lng']

    if travel_data is not None:
        return travel.update(travel_data['travel_id'], origin_lat=origin_lat,
                             origin_lng=origin_lng, destination_lat=destination_lat,
                             destination_lng=destination_lng,
                             places_visiting=places_visiting, buddies=buddies,
                             vehicle=vehicle, fuel_fare=fuel_fare, hotel_fare=hotel_fare,
                             restaurant_fare=restaurant_fare, toll_fare=toll_fare,
                             miscellaneous_fare=miscellaneous_fare, share=share,
                             travel_type=travel_type)
