import datetime
import json
import hashlib

from flask import Blueprint, request, Response, jsonify

from Travlr import app, db
from Travlr.constants import constants
from Travlr.exceptions.data_not_found_exception import DataNotFoundException
from Travlr.exceptions.invalid_credentials_exception import InvalidCredentialsException
from Travlr.exceptions.user_already_exists_exception import UserAlreadyExistsException
from Travlr.user.model import User

views = Blueprint('views', __name__)
timestamp = datetime.datetime

@views.route('/view', methods = [constants.GET])
def view_users():
    """
    This method will retrieve all user details from the database
    :return: all user details
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        query = db.session.query(User).all()
        if query is None:
            app.logger.warning("User data is not available")
            raise DataNotFoundException("User data is not available", constants.CODE_404)
        else:
            app.logger.info("Fetching user data")
            return jsonify(query)


@views.route('/view-one/<email>', methods=[constants.GET])
def view_user(email):
    """
    This method will retrieve a single user data from the database
    :param email: email id of the user
    :return: single user detail
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        query = db.session.query(User).filter_by(email=email, is_deleted=0).first()
        if query is None:
            app.logger.warning("User data is not available")
            raise DataNotFoundException("User data is not available", constants.CODE_404)
        else:
            app.logger.info("Fetching user data")
            return jsonify(query)


@views.route('/login', methods = [constants.POST])
def login_user():
    data = request.json
    email = data['email']
    password = hashlib.md5(data['password'].encode()).hexdigest()
    with app.app_context():
        user = db.session.query(User).filter_by(email=email).first()
        if user is not None and user.password == password:
            return {
                constants.ID: user.id,
                constants.NAME: user.name,
                constants.EMAIL: user.email,
                constants.MOBILE_NUMBER: user.mobile_number,
                constants.GENDER: user.gender
            }
        else:
            app.logger.warning("Invalid username or password")
            raise InvalidCredentialsException("Invalid username or password",
                                              constants.CODE_401)


@views.route('/add', methods = [constants.POST])
def register_user():
    """
    This method will add a user detail into the database
    :return: added user detail
    """
    data = request.json
    name = data['name']
    email = data['email']
    password = hashlib.md5(data['password'].encode()).hexdigest()
    date_of_birth = data['date_of_birth']
    mobile_number = data['mobile_number']
    gender = data['gender']
    is_deleted = 0
    created_date = timestamp.now()
    app.logger.info("Adding user details to user table")
    with app.app_context():
        try:
            db.session.add(User(name=name, email=email, password=password,
                                date_of_birth=date_of_birth, mobile_number=mobile_number,
                                gender=gender, is_deleted=is_deleted,
                                created_date=created_date))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.warning("User already exists")
            raise UserAlreadyExistsException(e, constants.CODE_400)
    app.logger.info("Adding user details")
    return {
        constants.MESSAGE: "User added successfully",
        constants.STATUS_CODE: constants.CODE_200,
        constants.TIMESTAMP: timestamp.now()
    }


@views.route('/delete/<email>', methods = [constants.DELETE])
def delete_user(email):
    """
    This method will delete a user from the database
    :param email: user email
    :return: deleted user detail
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        user = db.session.query(User).filter_by(email=email).first()
        if user is not None:
            user.is_deleted = 1
            db.session.commit()
            app.logger.info(f"User deleted successfully - user_id: {user.id}")
            return {
                constants.ID: user.id,
                constants.STATUS_CODE: constants.CODE_200,
                constants.DESCRIPTION: 'User deleted successfully',
                constants.TIMESTAMP: str(timestamp.now())
            }
    app.logger.warn(f"No user found - email_id: {email}")
    raise DataNotFoundException("User data not found", constants.CODE_404)


@views.route('/update/<email>', methods = [constants.PATCH])
def update_user(email):
    """
    This method will update a user based on the email
    :param email: email of the user to update
    :return: updated user detail
    :raise DataNotFoundException: if the data is not found
    """
    data = request.json
    name = data.get('name')
    password = data.get('password')
    date_of_birth = data.get('date_of_birth')
    mobile_number = data.get('mobile_number')
    gender = data.get('gender')
    with app.app_context():
        user = db.session.query(User).filter_by(email=email, is_deleted=0).first()
        if name is not None:
            user.name = name
            app.logger.info("Updated name")
        if password is not None:
            user.password = password
            app.logger.info("Updated password")
        if date_of_birth is not None:
            user.date_of_birth = date_of_birth
            app.logger.info("Updated date_of_birth")
        if mobile_number is not None:
            user.mobile_number = mobile_number
            app.logger.info("Updated mobile_number")
        if gender is not None:
            user.gender = gender
            app.logger.info("Updated gender")
        if user is not None:
            user.updated_date = timestamp.now()
            app.logger.info("Updated updated_date")
            db.session.commit()
            app.logger.info("Updated user")
        else:
            app.logger.warning("User data not found", constants.CODE_404)
            raise DataNotFoundException("User data not found", constants.CODE_404)
    return json.dumps(user)