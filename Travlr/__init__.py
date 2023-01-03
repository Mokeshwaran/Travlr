import os

from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from Travlr.user import views as user_views
    from Travlr.travel import views as travel_views
    from Travlr.vehicle import views as vehicle_views

    app.register_blueprint(user_views.views, name='user_views', url_prefix='/user')
    app.register_blueprint(travel_views.views, name='travel_views', url_prefix='/travel')
    app.register_blueprint(vehicle_views.views, name='vehicle_views', url_prefix='/vehicle')

    with app.app_context():
        db.create_all()
        return app

app = create_app()

if __name__ == '__main__':
    app.run(port=8000, debug=True)
