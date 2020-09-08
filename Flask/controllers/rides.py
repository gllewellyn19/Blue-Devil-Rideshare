from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from sqlalchemy import distinct, update, create_engine
from datetime import date
from database import db
import pdb
import os
from sqlalchemy.orm import sessionmaker
import datetime
import requests
import forms
import models
from mainRideFunctionHelpers import search_rides
from mainRideFunctionHelpers import ride_reservations
from mainRideFunctionHelpers import ride_postings
from registrationLogInHelpers import sign_up
from registrationLogInHelpers import make_driver
from registrationLogInHelpers import log_in
from accountPageHelpers import account
from accountPageHelpers import edit_info
from accountPageHelpers import check_ride_num
from accountPageHelpers import edit_ride
from accountPageHelpers import edit_reservation
from accountPageHelpers import riders_contact_info
from accountPageHelpers import previous_rides
from accountPageHelpers import previous_reservations

bp = Blueprint('rides', __name__, url_prefix = '/rides', template_folder = 'templates')

@bp.route('/')
def home_page():
    return render_template('basicRidePages/home.html')

@bp.route('/find-rides', methods=['GET', 'POST'])
def find_rides_main():
    return search_rides.find()

@bp.route('/reserve-rides', methods=['GET', 'POST'])    
def reserve_ride_main():  
    return ride_reservations.reserve(request.args.get('rideNo'), int(request.args.get('spots_needed')))

@bp.route('/list-rides', methods=['GET', 'POST'])
def list_rides_main():
    return ride_postings.list_ride()

@bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up_main():
    return sign_up.create_account()

@bp.route('/register-driver', methods=['GET', 'POST'])
def register_driver_main():
    return make_driver.register()

@bp.route('/log-in', methods=['GET', 'POST'])
def log_in_main():
    return log_in.sign_in()
    
@bp.route("/logout")
def log_out():
    session['logged_in'] = False
    session['netid'] = None
    session['driver'] = False
    return home_page()

@bp.route('/account')
def account_main():
    return account.account_info()
    
@bp.route('/edit-info', methods=['GET', 'POST'])
def edit_info_main():
    return edit_info.update()

@bp.route('/edit-ride', methods=['GET', 'POST'])
def edit_ride_main():
    return edit_ride.edit()

#calls the necessary functions after the ride number is verified 
@bp.route('/verify-ride-number', methods=['GET', 'POST'])
def verify_ride_main():
    return check_ride_num.verify()
    
@bp.route('/edit-reservation', methods=['GET', 'POST'])
def edit_rev_main():
    return edit_reservation.edit()

@bp.route('/riders-netids')
def riders_netids_main():
    return riders_contact_info.get_info()

@bp.route('/past-rides')
def past_rides_main():
    return previous_rides.get_prev_rides()

@bp.route('/past-reservations')
def past_reservations_main():
    return previous_reservations.get_prev_revs() 

    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug = True)
