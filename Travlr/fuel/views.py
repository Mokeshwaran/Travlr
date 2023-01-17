from flask import Blueprint, jsonify

from Travlr.constants import constants
from Travlr.exceptions.data_not_found_exception import DataNotFoundException
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

from Travlr import app, db
from Travlr.fuel.model import Fuel

timestamp = datetime.datetime
options = Options()
options.headless = True
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                          options=options)
views = Blueprint('views', __name__)


@views.route('/view', methods = [constants.GET])
def view_fuels():
    """
    This method will retrieve the fuel data from the database
    :return: all fuel details
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        query = db.session.query(Fuel).all()
        if not query:
            app.logger.warning("Fuel data is not available")
            raise DataNotFoundException("Fuel data is not available", 404)
        else:
            app.logger.info("Fetching fuel data")
            return jsonify(query)


def add_petrol(fuel_table, query):
    """
    This method will add the petrol data to the database
    :param fuel_table: table of fuel data
    :param query: queried result of table data
    """
    for key, val in fuel_table.items():
        district_name = key
        fuel_type = constants.PETROL
        fuel_price = float(fuel_table[key]['fuel_price'][:6])
        fuel_data = query.filter(Fuel.district_name == district_name,
                                 Fuel.fuel_type == fuel_type)
        if fuel_data.first() is None:
            app.logger.info("Adding petrol data")
            db.session.add(Fuel(district_name=district_name, fuel_type=fuel_type,
                                fuel_price=fuel_price, created_date=timestamp.now(),
                                created_by=constants.ADMIN))
            db.session.commit()
            app.logger.info("Added petrol data")
        else:
            app.logger.info("Updating petrol data")
            fuel_data.update({
                'fuel_price': fuel_price,
                'updated_date': timestamp.now(),
                'updated_by': constants.ADMIN
            }, synchronize_session='fetch')
            db.session.commit()
            app.logger.info("Updated petrol data")
        app.logger.info(f"Posted petrol data - district_name: {key}")


def add_diesel(fuel_table, query):
    """
    This method will add diesel data to the database
    :param fuel_table: table of fuel data
    :param query: queried results of fuel_table
    """
    for key, val in fuel_table.items():
        district_name = key
        fuel_type = constants.DIESEL
        fuel_price = float(fuel_table[key]['fuel_price'][:5])
        fuel_data = query.filter(Fuel.district_name == district_name,
                                 Fuel.fuel_type == fuel_type)
        if fuel_data.first() is None:
            app.logger.info("Adding diesel data")
            db.session.add(Fuel(district_name=district_name, fuel_type=fuel_type,
                                fuel_price=fuel_price, created_date=timestamp.now(),
                                created_by=constants.ADMIN))
            db.session.commit()
            app.logger.info("Added diesel data")
        else:
            app.logger.info("Updating diesel data")
            fuel_data.update({
                'fuel_price': fuel_price,
                'updated_date': timestamp.now(),
                'updated_by' : constants.ADMIN
            }, synchronize_session='fetch')
            db.session.commit()
            app.logger.info("Updated diesel data")
        app.logger.info(f"Posted diesel data - district_name: {key}")


@views.route('/add', methods = [constants.POST])
def add_fuel():
    """
    This method will add the fuel detail to the database
    :return: added successfully response
    """
    with app.app_context():
        query = db.session.query(Fuel)
        app.logger.info("Fetching petrol data")
        fuel_table = get_petrol()
        add_petrol(fuel_table, query)

        app.logger.info("Fetching diesel data")
        fuel_table = get_diesel()
        add_diesel(fuel_table, query)
        return "Added successfully"


def get_diesel():
    """
    This method will get and post the diesel data scraped from the web.
    :return: JSON content of diesel data
    """
    app.logger.info("Fetching diesel data")
    driver.get(constants.DIESEL_URL)
    # Finding the element using xpath and getting its HTML
    table = driver.find_element(By.XPATH, constants.XPATH) \
        .get_attribute('outerHTML')

    diesel_table = pd.read_html(table)[0]
    # Renaming columns of the table for the database
    diesel_table.rename(columns={
        'City/District': 'district_name',
        'Price': 'fuel_price'
    }, inplace=True)
    # Removing unnecessary column from the table
    diesel_table.pop('Change')
    diesel_table['fuel_type'] = constants.DIESEL
    # Setting district_name as key and other rows as values and converting to dict
    diesel_table = diesel_table.set_index('district_name').to_dict(orient='index')
    app.logger.info("Fetched diesel data")
    return diesel_table


def get_petrol():
    """
    This method will get and post the petrol data scraped from the web.
    :return: JSON content of petrol data
    """
    app.logger.info("Fetching petrol data")
    driver.get(constants.PETROL_URL)
    # Finding the element using xpath and getting its HTML
    table = driver.find_element(By.XPATH, constants.XPATH) \
        .get_attribute('outerHTML')

    petrol_table = pd.read_html(table)[0]
    # Renaming columns of the table for the database
    petrol_table.rename(columns={
        'City/District': 'district_name',
        'Price': 'fuel_price'
    }, inplace=True)
    # Removing unnecessary column from the table
    petrol_table.pop('Change')
    petrol_table['fuel_type'] = constants.PETROL
    # Setting district_name as key and other rows as values and converting to dict
    petrol_table = petrol_table.set_index('district_name').to_dict(orient='index')
    app.logger.info("Fetched petrol data")
    return petrol_table
