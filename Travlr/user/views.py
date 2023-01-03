import json

from flask import Blueprint, request, jsonify
from Travlr.user.model import User

views = Blueprint('views', __name__)
user = User()
@views.route('/view', methods = ['GET'])
def view_users():
    return user.get()

@views.route('/view-one', methods = ['GET'])
def view_user():
    email_id = request.json['email_id']
    return jsonify(json.loads(user.get_user(email_id)))

@views.route('/add', methods = ['POST'])
def add_user():
    data = request.json
    name = data['name']
    email_id = data['email_id']
    password = data['password']
    date_of_birth = data['date_of_birth']
    mobile_number = data['mobile_number']
    gender = data['gender']
    return user.post(name=name, email_id=email_id, password=password,
                     date_of_birth=date_of_birth, mobile_number=mobile_number,
                     gender=gender)

@views.route('/delete', methods = ['DELETE'])
def delete_user():
    email_id = request.json['email_id']
    return user.delete(email_id)

@views.route('/update/<email_id>', methods = ['PATCH'])
def update_user(email_id):
    data = request.json
    user_data = json.loads(user.get_user(email_id))
    name = data.get('name')
    password = data.get('password')
    date_of_birth = data.get('date_of_birth')
    mobile_number = data.get('mobile_number')
    gender = data.get('gender')

    if user_data is not None:
        return user.update(user_data['user_id'], name, password, date_of_birth,
                           mobile_number, gender)