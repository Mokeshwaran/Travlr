import datetime
import uuid
from typing import Any

import pandas as pd

from flask import Blueprint, jsonify, Response
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from Travlr.constants import constants
from Travlr.exceptions.data_not_found_exception import DataNotFoundException
from Travlr import app, db
from Travlr.fuel.model import Fuel

timestamp = datetime.datetime
options = Options()
options.headless = True
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                          options=options)
views = Blueprint('views', __name__)


@views.route('/view', methods = [constants.GET])
def view_fuels() -> Response:
    """
    This method will retrieve the fuel data from the database
    :return: all fuel details
    :raise DataNotFoundException: if the data is not found
    """
    with app.app_context():
        query = db.session.query(Fuel).all()
        if not query:
            app.logger.warning("Fuel data is not available")
            raise DataNotFoundException("Fuel data is not available", constants.CODE_404)
        else:
            app.logger.info("Fetching fuel data")
            return jsonify(query)


def add_petrol(fuel_table: dict, query: Any) -> None:
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
                constants.FUEL_PRICE: fuel_price,
                constants.UPDATED_DATE: timestamp.now(),
                constants.UPDATED_BY: constants.ADMIN
            }, synchronize_session=constants.FETCH)
            db.session.commit()
            app.logger.info("Updated petrol data")
        app.logger.info(f"Posted petrol data - district_name: {key}")


def add_diesel(fuel_table: dict, query: Any) -> None:
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
                                created_by=constants.ADMIN_ID))
            db.session.commit()
            app.logger.info("Added diesel data")
        else:
            app.logger.info("Updating diesel data")
            fuel_data.update({
                constants.FUEL_PRICE: fuel_price,
                constants.UPDATED_DATE: timestamp.now(),
                constants.UPDATED_BY: constants.ADMIN_ID
            }, synchronize_session=constants.FETCH)
            db.session.commit()
            app.logger.info("Updated diesel data")
        app.logger.info(f"Posted diesel data - district_name: {key}")


@views.route('/add', methods = [constants.POST])
def add_fuel() -> Response:
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
        return jsonify({
            constants.ID: str(uuid.uuid1()),
            constants.DESCRIPTION: "Fuel added successfully",
            constants.STATUS_CODE: constants.CODE_200
        })


def get_diesel() -> dict:
    """
    This method will get and post the diesel data scraped from the web.
    :return: JSON content of diesel data
    """
    app.logger.info("Fetching diesel data")
    driver.get(constants.DIESEL_URL)
    # Finding the element using xpath and getting its HTML
    table = driver.find_element(By.XPATH, constants.XPATH) \
        .get_attribute(constants.OUTER_HTML)

    driver.get(constants.DIESEL_URL_UT)
    # Finding the element using xpath and getting its HTML
    table_ut = driver.find_element(By.XPATH, constants.XPATH) \
        .get_attribute(constants.OUTER_HTML)

    diesel_table = pd.read_html(table)[0]
    diesel_table_ut = pd.read_html(table_ut)[0]
    diesel_table = pd.concat([diesel_table, diesel_table_ut])
    # Renaming columns of the table for the database
    diesel_table.rename(columns={
        constants.CITY_DISTRICT: constants.DISTRICT_NAME,
        constants.PRICE: constants.FUEL_PRICE
    }, inplace=True)
    standardize_district_name(diesel_table)
    # Removing unnecessary column from the table
    diesel_table.pop(constants.CHANGE)
    diesel_table['fuel_type'] = constants.DIESEL
    # Setting district_name as key and other rows as values and converting to dict
    diesel_table = diesel_table.set_index(constants.DISTRICT_NAME)\
        .to_dict(orient=constants.INDEX)
    app.logger.info("Fetched diesel data")
    return diesel_table


def get_petrol() -> dict:
    """
    This method will get and post the petrol data scraped from the web.
    :return: JSON content of petrol data
    """
    app.logger.info("Fetching petrol data")
    driver.get(constants.PETROL_URL)
    # Finding the element using xpath and getting its HTML
    table = driver.find_element(By.XPATH, constants.XPATH) \
        .get_attribute(constants.OUTER_HTML)

    driver.get(constants.PETROL_URL_UT)
    # Finding the element using xpath and getting its HTML
    table_ut = driver.find_element(By.XPATH, constants.XPATH) \
        .get_attribute(constants.OUTER_HTML)

    petrol_table = pd.read_html(table)[0]
    petrol_table_ut = pd.read_html(table_ut)[0]
    petrol_table = pd.concat([petrol_table, petrol_table_ut])
    # Renaming columns of the table for the database
    petrol_table.rename(columns={
        constants.CITY_DISTRICT: constants.DISTRICT_NAME,
        constants.PRICE: constants.FUEL_PRICE
    }, inplace=True)
    standardize_district_name(petrol_table)
    # Removing unnecessary column from the table
    petrol_table.pop(constants.CHANGE)
    petrol_table['fuel_type'] = constants.PETROL
    # Setting district_name as key and other rows as values and converting to dict
    petrol_table = petrol_table.set_index(constants.DISTRICT_NAME)\
        .to_dict(orient=constants.INDEX)
    app.logger.info("Fetched petrol data")
    return petrol_table

def standardize_district_name(fuel_table: DataFrame) -> None:
    """
    This method will standardize wrongly spelled district names.
    :param fuel_table: table of petrol data
    """
    fuel_table.loc[
        fuel_table[constants.DISTRICT_NAME] == "Kanchipuram", constants.DISTRICT_NAME
    ] = "Kancheepuram"

    fuel_table.loc[
        fuel_table[constants.DISTRICT_NAME] == "Kanniyakumari", constants.DISTRICT_NAME
    ] = "Kanyakumari"

    fuel_table.loc[
        fuel_table[constants.DISTRICT_NAME] == "Teni", constants.DISTRICT_NAME
    ] = "Theni"

    fuel_table.loc[
        fuel_table[constants.DISTRICT_NAME] == "Tiruchchirappalli",
        constants.DISTRICT_NAME
    ] = "Tiruchirappalli"

    fuel_table.loc[
        fuel_table[constants.DISTRICT_NAME] == "Tirupur", constants.DISTRICT_NAME
    ] = "Tiruppur"

    fuel_table.loc[
        fuel_table[constants.DISTRICT_NAME] == "Tiruvallur", constants.DISTRICT_NAME
    ] = "Thiruvallur"

    fuel_table.loc[
        fuel_table[constants.DISTRICT_NAME] == "Tuticorin", constants.DISTRICT_NAME
    ] = "Thoothukudi"

    fuel_table.loc[
        fuel_table[constants.DISTRICT_NAME] == "Virudunagar", constants.DISTRICT_NAME
    ] = "Virudhunagar"

    fuel_table.loc[
        fuel_table[constants.DISTRICT_NAME] == "Pondicherry", constants.DISTRICT_NAME
    ] = "Puducherry"
