import datetime
import hashlib
import os
from logging.config import dictConfig

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from Travlr.constants import constants
from Travlr.exceptions.api_exception import APIException

timestamp = datetime.datetime

load_dotenv()
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file_handler': {
            'class' : 'logging.FileHandler',
            'formatter': 'default',
            'filename' : 'Travlr.log',
            'level'    : 'INFO'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file_handler']
    }
})

app = Flask(__name__)
app.logger.handlers.clear()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate()
migrate.init_app(app, db)

from Travlr.user import views as user_views
from Travlr.travel import views as travel_views
from Travlr.vehicle import views as vehicle_views
from Travlr.fuel import views as fuel_views
from Travlr.location import views as location_views
from Travlr.expense import views as expense_views

app.register_blueprint(user_views.views, name='user_views', url_prefix='/user')
app.register_blueprint(travel_views.views, name='travel_views', url_prefix='/travel')
app.register_blueprint(vehicle_views.views, name='vehicle_views', url_prefix='/vehicle')
app.register_blueprint(fuel_views.views, name='fuel_views', url_prefix='/fuel')
app.register_blueprint(location_views.views, name='location_views', url_prefix='/location')
app.register_blueprint(expense_views.views, name='expense_views', url_prefix='/expense')

@app.errorhandler(APIException)
def exception_handler(err):
    """
    This method handles exception raised by any method in the program
    :param err: error details from a method
    :return: error response to the user
    """
    response = {
        constants.ERROR: err.description,
        constants.STATUS_CODE: err.code,
        constants.TIMESTAMP: timestamp.now()
    }
    data = hashlib.md5(request.get_data(as_text=True, cache=False).encode()).hexdigest()
    app.logger.error(f'{err.description} - {request.url_root} - '
                     f'{data}: {response["status_code"]}')
    return jsonify(response), err.code

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(port=8080, debug=True)
