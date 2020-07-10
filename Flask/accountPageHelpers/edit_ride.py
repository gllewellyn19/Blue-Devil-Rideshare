from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for, render_template

import forms
import models

def edit():
    """
    Edits a ride that the user is already driving
    """
    rideNo=request.args.get('rideNo')
    editRideForm=forms.EditRideFactory()
    ride=None
    userDrivingRide=check_user_driving_ride(rideNo)

    #only perform the following if the logged in user is driving this ride
    if userDrivingRide:
        ride=set_defaults(rideNo, editRideForm)

        if editRideForm.validate_on_submit():
            cancel = request.form['cancel']

            if cancel == "Yes":
                delete_ride(ride)
            else:
                #this means the ride failed to update (time or date invalid)- if it didn't fail then this function updated the ride
                if not update_ride(ride, editRideForm):
                    return redirect(url_for('rides.edit_ride_main', rideNo=rideNo))
            return redirect(url_for('rides.account_main'))

    return render_template('accountPages/edit-ride.html', form=editRideForm, ride=ride, userDrivingRide=userDrivingRide)

def check_user_driving_ride(rideNo):
    """
    Double check the current user is the one driving the ride (preventing malicious input from people changing URLs)
    Return true if the current user is who is driving this ride
    """
    
    #means the user isn't logged in and should not be able to perform this function
    if session['netid']==None:
        return False

    #check if they are driving the ride number given
    db.session.execute('''PREPARE Ride (integer, varchar) AS SELECT * FROM Ride WHERE ride_no = $1 AND driver_netid = $2;''')
    ride=[]
    ride.extend(db.session.execute('EXECUTE Ride(:ride_no, :netid)', {"ride_no":rideNo, "netid":session['netid']}))
    db.session.execute('DEALLOCATE Ride')
    return ride != []

def set_defaults(rideNo, editRideForm):
    """
    Sets the defaults for the ride form
    """
    ride=db.session.query(models.Ride).filter(models.Ride.ride_no == rideNo).first()
    editRideForm.earliest_departure.data=ride.earliest_departure
    editRideForm.latest_departure.data=ride.latest_departure
    editRideForm.date.data=ride.date
    return ride

def delete_ride(ride):
    """
    Deletes the ride and all reservations for the ride
    """
    reservationsToDelete = db.session.query(models.Reserve).filter(models.Reserve.ride_no == ride.ride_no)
    for reservation in reservationsToDelete:
        db.session.delete(reservation)
        db.session.commit()
    db.session.delete(ride)
    db.session.commit()
    flash("Ride cancelled.")

def update_ride(ride, form):
    """
    Updates the ride after making sure the date and times are valid (returns false if they aren't)
    """
    newdate=request.form['date']
    newearliest_departure = request.form['earliest_departure']
    newlatest_departure = request.form['latest_departure']
    #check to make sure latest departure after earliest departure and user doesn't have ride/reservation on the date
    if not check_times_valid(newearliest_departure, newlatest_departure) or not check_date_valid(newdate, ride.ride_no):
        return False
    newgas_price = request.form['gas_price']
    newcomments = request.form['comments']
            
    ride.gas_price = newgas_price
    ride.comments = newcomments
    ride.earliest_departure = newearliest_departure
    ride.latest_departure = newlatest_departure
    ride.date = newdate
    db.session.commit()
    flash("Ride updated.")
    return True

def check_times_valid(earliest_departure, latest_departure):
    """
    Checks to make sure the earliest departure is before the latest departure (returns true if valid)
    """
    if earliest_departure > latest_departure:
        flash("Earliest departure must be before latest departure")
        return False
    return True

def check_date_valid(date, rideNo):
    """
    Checks to make sure that the date is after today's date and driver doesn't have a ride on that day (returns true if valid)
    """
    if date < str(datetime.date.today()):
        flash("Date must be greater than or equal to "+ str(datetime.date.today()))
        return False
    if check_rides_on_date(date, rideNo):
        flash("You are already driving a ride on this date- please choose another date")
        return False
    if check_revs_on_date(date):
        flash("You already have a reservation on this date- please choose another date")
        return False
    return True

def check_rides_on_date(date, rideNo):
    """
    Returns true if the driver is alredy driving a ride on the given date which means they can't drive another
    """
    ridesOnDate=[]
    db.session.execute('''PREPARE ridesOnDate (varchar, date) AS SELECT * FROM Ride WHERE driver_netid = $1 AND date= $2 AND ride_no!=$3;''')
    ridesOnDate.extend(db.session.execute('EXECUTE ridesOnDate(:driver_netid, :date, :ride_no)', {"driver_netid":session['netid'], "date":date, "ride_no":rideNo}))
    db.session.execute('DEALLOCATE ridesOnDate')
    return ridesOnDate!=[]

def check_revs_on_date(date):
    """
    Returns true if the driver already has a reservation on the given date which means they can't drive a ride too
    """
    revsOnDate=[]
    db.session.execute('''PREPARE revsOnDate (varchar, date) AS SELECT * FROM Reserve rev WHERE rev.rider_netid = $1\
            AND EXISTS (SELECT * FROM Ride r WHERE r.ride_no=rev.ride_no and r.date=$2);''')
    revsOnDate.extend(db.session.execute('EXECUTE revsOnDate(:driver_netid, :date)', {"driver_netid":session['netid'], "date":date}))
    db.session.execute('DEALLOCATE revsOnDate')
    return revsOnDate!=[]

