
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

#app = Flask(__name__)
#app.secret_key = 's3cr3t' #change this?
#app.config.from_object('config')

#db = SQLAlchemy(app, session_options={'autocommit': False})

import forms
import models
import findRides
import reserveRides
import listRides
import signUp
import registerDriver
import logIn
import account

#global variables
rideToEdit = None
reservationToEdit = None
rideToEditTime = None

bp = Blueprint('rides', __name__, url_prefix = '/rides', template_folder = 'templates')

@bp.route('/')
def home_page():
    return render_template('home.html')


#NOTE: SHOULDN'T NEED BOTH FORMS
@bp.route('/find-rides', methods=('GET', 'POST'))
def find_rides_main():
    spotsNeeded,searchForm,reserveForm,results = findRides.find_rides()
    #redo with validators
    if searchForm==None:
        return redirect(url_for('rides.find_rides_main'))
    return render_template('find-rides.html', searchForm=searchForm, reserveForm=reserveForm, results=results, spotsNeeded=spotsNeeded) 

@bp.route('/reserve-rides', methods=('GET', 'POST'))    
def reserveRide_main():  
#def reserveRide_main(rideNo, spotsNeeded):
    rideNo=4161
    spotsNeeded=1
    ride,searchForm,reserveForm=reserveRides.reserve_rides(rideNo, spotsNeeded)
    return render_template('reserve-rides.html', searchForm=searchForm, reserveForm = reserveForm, ride=ride)


@bp.route('/list-rides', methods=['GET','POST'])
def list_rides_main():
    form = forms.ListRideFormFactory()
    listRides.list_rides(form)
    return render_template('list-rides.html', form=form)

@bp.route('/sign-up', methods=['GET','POST'])
def sign_up_main():
    #NOTE: maybe change this return statement
    signupForm = forms.RegisterFormFactory()
    toReturn = signUp.sign_up(signupForm)
    return toReturn
    #return render_template('sign-up.html', form=signupForm)

@bp.route('/register-driver', methods=['GET','POST'])
def register_driver_main():
    registerDriverForm = forms.RegisterDriverFormFactory()
    returnStatement = registerDriver.register_driver(registerDriverForm)
    return returnStatement
    

@bp.route('/log-in', methods=['GET','POST'])
def log_in_main():
    toReturnStatement = logIn.log_in()
    return toReturnStatement
    

@bp.route("/logout")
def log_out():
    session['logged_in'] = False
    session['netid'] = None
    session['driver'] = False
    return home_page()

@bp.route('/account', methods=('GET', 'POST'))
def account_main():
    user,driver,ridesListed,reservations,rideToday,revToday = account.account()
    return render_template('account.html', user=user, driver=driver, ridesListed=ridesListed, reservations=reservations, rideToday=rideToday,revToday=revToday)

@bp.route('/edit-info', methods=('GET', 'POST'))
def editInfo():
    #user = models.Rideshare_user.query.filter_by(netid=session['netid']).first()
    user = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).first()
    form = forms.EditInfoFactory()
    #driver = models.Driver.query.filter_by(netid=session['netid']).first()
    driver = db.session.query(models.Driver).filter(models.Driver.netid == session['netid']).first()
    if form.validate_on_submit():
        newphone_number=request.form['phone_number']
        #note should I update so they can choose affiliation and school?
        #newaffiliation=request.form['affiliation']
        #newschool=request.form['school']
        #dont need to check if equal to confirm because form does that for me
        if driver !=None:
            plateNum = request.form['license_plate_no']
            plateState = request.form['plate_state']
        else:
            plateNum=None
            plateState=None
        currentpassword = request.form['currentPassword']
        newpassword=request.form['password']
        confirmpassword = request.form['confirmPassword']
        #should be validator when phone number is a string
        if len(str(newphone_number))<6 or len(str(newphone_number))>10:
            flash("Your phone number must be at least 6 characters and no more than 10.")
            return redirect(url_for('rides.editInfo'))
        if plateNum!=None and (len(plateNum)<2 or len(plateNum)>10):
            flash("Your plate number must be at least 2 characters and no more than 10.")
            return redirect(url_for('rides.editInfo'))
        #if platenum is null and driver
        
        if currentpassword != user.password:
            flash("Password doesn't match current password. Changes could not be made.")
            return redirect(url_for('rides.editInfo'))

        user_edit = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).one()
        driver_edit = db.session.query(models.Driver).filter(models.Driver.netid == session['netid']).first()

        #if new password field wasn't empty then new password is equal to confirm password- only update password in this case
        if plateNum == None and driver_edit !=None:
            flash("Must enter plate number")
            return redirect(url_for('rides.editInfo'))
        if newpassword != '':
            if len(newpassword)<5 or len(newpassword)>100:
                flash("Your new password must be at least 5 characters and no more than 100")
                return redirect(url_for('rides.editInfo'))
            if newpassword != user.password:
                flash("Password updated.") 
            user_edit.password = newpassword
        #can just do this even if they do not make any changes
        user_edit.phone_number = newphone_number
        db.session.commit()
        
        if driver_edit == None:
            flash("User information updated.")
            return redirect(url_for('rides.account')) 

        driver_edit.license_plate_no = plateNum
        if plateState != 'No Change':
            driver_edit.plate_state = plateState
        db.session.commit()
        driver_edit.license_plate_no = plateNum
        if plateState != 'No Change':
            driver_edit.plate_state = plateState
        db.session.commit()
        #user_edit.affiliation = newaffiliation
        #user_edit.school = newschool
        
        flash("User information updated.")
        return redirect(url_for('rides.account'))

    
    return render_template('edit-info.html', user=user, debug=True, form=form, driver=driver)
    
@bp.route('/edit-list-ride-rideNo-Check', methods=('GET', 'POST'))
def editRidesRideNoCheck():
    form = forms.EditRideFactory()
    formRideNo = forms.RideNumberFactory()
    #cancelForm = forms.CancelRideFactory()
    validRideNo = False
    ride = None
    
    
    if formRideNo.validate_on_submit():
        rideNumber = request.form['ride_no']
        global rideToEdit
        rideToEdit = db.session.query(models.Ride) \
                    .filter(models.Ride.ride_no == rideNumber) \
                    .filter(models.Ride.driver_netid == session['netid']).first()
        ride = rideToEdit
        if (ride == None):
            flash("Ride not found.")
            return redirect(url_for('rides.account'))
        else: 
            print(ride.earliest_time)
            validRideNo = True

    return render_template('edit-list-ride.html', form=form, formRideNo=formRideNo, validRideNo = validRideNo, ride=ride)

@bp.route('/edit-list-ride', methods=('GET', 'POST'))
def editRides():
    form = forms.EditRideFactory()
    formRideNo = forms.RideNumberFactory()
    #cancelForm = forms.CancelRideFactory()
    validRideNo = True
    ride = None
    
    if form.validate_on_submit():
        ride = rideToEdit
        print(rideToEdit.comments)

        #figure out who the edits affect
        #reservesAffected = models.Reserve.query.filter_by(ride_no=rideToEdit.ride_no)
        #netIDsAffected = None
        #for reservation in reservesAffected:
            #netIDsAffected.append(reservation.rider_netid)
        #could I check net ids affected with??
        #ADD BACK IN LATER
        #if (netIDsAffected != None):
            #for netidAffected in netIDsAffected:
                #session['netidAffected']
                #flash("One of your reserved rides has changed")
        #print(netIDsAffected.first())

        rideNumber = rideToEdit.ride_no
        cancel = request.form['cancel']
        if cancel == "Yes":
            #how to delete a ride?
            reservationsToDelete = db.session.query(models.Reserve).filter(models.Reserve.ride_no == rideNumber)
            for reservation in reservationsToDelete:
                db.session.delete(reservation)
                db.session.commit()
            db.session.delete(rideToEdit)
            db.session.commit()
            print("ride cancelled")
            flash("Ride cancelled.")
        else:
           # newearliest_departure = request.form['earliest_departure']
            #newlatest_departure = request.form['latest_departure']
            newgas_price = request.form['gas_price']
            newcomments = request.form['comments']

            if newgas_price == '':
                newgas_price = None
            if newcomments=='':
                newcomments = None
            
            edit_ride = db.session.query(models.Ride).filter(models.Ride.ride_no == rideNumber).one()
            edit_ride.gas_price = newgas_price
            edit_ride.comments = newcomments
            #edit_ride.earliest_time = newearliest_departure
            #edit_ride.latest_time = newlatest_departure
            db.session.commit()
            flash("Ride updated.")

        return redirect(url_for('rides.account'))

    return render_template('edit-list-ride.html', form=form, formRideNo=formRideNo, validRideNo = validRideNo, ride=ride)


@bp.route('/edit-reservation', methods=('GET', 'POST'))
def editReservation():
    #user = models.Rideshare_user.query.filter_by(netid=session['netid']).first()
    user = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).first()
    form = forms.EditReservationFactory()
    formRideNo = forms.RideNumberFactory()
    reservation = None
    validRideNo = False

    if formRideNo.validate_on_submit():
        rideNumber = request.form['ride_no']
        global reservationToEdit
        reservationToEdit = db.session.query(models.Reserve) \
                    .filter(models.Reserve.ride_no == rideNumber) \
                    .filter(models.Reserve.rider_netid == session['netid']).first()
        reservation = reservationToEdit
        if (reservation == None):
            flash("Reservation not found.")
            return redirect(url_for('rides.account'))
        else: 
            validRideNo = True

    if form.validate_on_submit():
        cancel = request.form['cancel']
        newSpots = 0
        rideNumber = reservationToEdit.ride_no
        ride = db.session.query(models.Ride).filter(models.Ride.ride_no == rideNumber).first()

        if cancel == "Yes":
            #how to delete a ride?
            newSpots = reservationToEdit.seats_needed*-1
            db.session.delete(reservationToEdit)
            db.session.commit()
            flash("Reservation cancelled.")
        #not cancelling-edit reservation
        else:
            updatedSpots = int(request.form['spots_needed'])
            newSpots = updatedSpots - reservationToEdit.seats_needed
            if (updatedSpots > ride.seats_available):
                flash("Not enough room in the ride for spots needed. Reservation not updated.")
                return redirect(url_for('rides.account'))
            reservation_edit = db.session.query(models.Reserve).filter(models.Reserve.ride_no == rideNumber).filter(models.Reserve.rider_netid == session['netid']).first()
            reservation_edit.seats_needed = updatedSpots
            db.session.commit()
            flash("Reservation updated.")
        #edit seats available no matter what
        ride_edit = db.session.query(models.Ride).filter(models.Ride.ride_no == rideNumber).one()
        ride_edit.seats_available = ride.seats_available - newSpots
        db.session.commit()
        
        
        return redirect(url_for('rides.account'))
        #except BaseException as e:
            #form.errors['database'] = str(e) #could be wrong

        #return redirect(url_for('rides.account'))
    
    return render_template('edit-reservation.html', user=user, debug=True, form=form, validRideNo=validRideNo, formRideNo=formRideNo, reservation=reservation)

@bp.route('/riders-netids', methods=('GET', 'POST'))
def Riders_Netids():
    form = forms.RideNetIdNumberFactory()
    validRideNo = False
    ride = None
    reservations = None
    rideNumber = None
    
    if form.validate_on_submit():
        rideNumber = request.form['ride_no']
        ride = db.session.query(models.Ride).filter(models.Ride.ride_no == rideNumber).filter(models.Ride.driver_netid == session['netid']).first()
        if (ride == None):
            flash("Ride not found.")
            return redirect(url_for('rides.account'))
        else: 
            validRideNo = True
            reservations = db.session.query(models.Reserve).filter(models.Reserve.ride_no == ride.ride_no)
            if reservations.first() == None:
                reservations = None

    return render_template('riders-netids.html', form=form, validRideNo = validRideNo, reservations=reservations, rideNumber=rideNumber)

@bp.route('/edit-ride-time-rideNo-check', methods=('GET', 'POST'))
def editRideTimeRideNoCheck():
    form = forms.EditRideTimeFactory()
    formRideNo = forms.RideNumberFactory()
    validRideNo = False
    ride = None
    validatingRideNo = False

    print("in edit ride time ride no check")
    
    if formRideNo.validate_on_submit():
        print("ride check validated")
        validatingRideNo = True
        rideNumber = request.form['ride_no']
        global rideToEditTime
        rideToEditTime = db.session.query(models.Ride) \
                    .filter(models.Ride.ride_no == rideNumber) \
                    .filter(models.Ride.driver_netid == session['netid']).first()
        ride = rideToEditTime
        
        if (ride == None):
            flash("Ride not found.")
            return redirect(url_for('rides.account'))
        reservations = db.session.query(models.Reserve).filter(models.Reserve.ride_no == rideNumber)
        if reservations.first() == None:
            reservations = None
        if not (reservations == None): #check if people already reserved this
            flash("You cannot change the time of ride people have already reserved. Please coordinate with them directly. You can find their netids via the form on the right.")
            return redirect(url_for('rides.account')) 
        else:
            validRideNo = True
    print("leaving valid ride number project")
    print(validRideNo)

    return render_template('edit-ride-time.html', form=form, formRideNo=formRideNo, validRideNo = validRideNo, ride=ride)

@bp.route('/edit-ride-time', methods=('GET', 'POST'))
def editRideTimeRide():
    form = forms.EditRideTimeFactory()
    formRideNo = forms.RideNumberFactory()
    validRideNo = True
    ride = None
    print("in edit ride time ride")

    if form.validate_on_submit():
        ride = rideToEditTime
        rideNumber = rideToEditTime.ride_no
        newearliest_departure = request.form['earliest_departure']
        newlatest_departure = request.form['latest_departure']
        #if newlatest_departure < newearliest_departure:
           # flash("Must make latest time of depature after earliest time of departure. Changes not saved.")
            #return redirect(url_for('rides.editRideTimeRide'))
        edit_ride = db.session.query(models.Ride).filter(models.Ride.ride_no == rideNumber).one()
        edit_ride.earliest_time = newearliest_departure
        edit_ride.latest_time = newlatest_departure
        db.session.commit()
        flash("Ride time updated.")
        return redirect(url_for('rides.account'))

    return render_template('edit-ride-time.html', form=form, formRideNo=formRideNo, validRideNo = validRideNo, ride=ride)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug = True)
