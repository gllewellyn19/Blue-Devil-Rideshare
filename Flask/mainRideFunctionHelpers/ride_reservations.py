from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for, render_template

import forms
import models


def reserve(rideNo, spots_needed):
    reserveForm = forms.ReserveRideFormFactory()
    ride = db.session.query(models.Ride).filter(models.Ride.ride_no == rideNo).first()

    if reserveForm.validate_on_submit():
        notes = request.form['notes']
        
        if spots_needed > ride.seats_available:
            flash("Not enough spots in this ride as the number of spots available changed since your request.")
            return redirect(url_for('rides.find_rides_main')) 
        
        if check_rides_on_date(ride.date):
            flash("You are already driving a ride on this day and can't reserve a ride.")
            return redirect(url_for('rides.find_rides_main'))

        if check_revs_on_date(ride.date):
            flash("You have already reserved a ride on this day and can't reserve another ride.")
            return redirect(url_for('rides.find_rides_main'))

        book_ride(ride, spots_needed, rideNo, notes)
        return redirect(url_for('rides.find_rides_main'))

    return render_template('basicRidePages/reserve-rides.html', reserveForm=reserveForm, ride=ride, spots_needed=spots_needed)

#returns true if the user is already driving a ride on that date (can't book a reservations)
def check_rides_on_date(date):
    myRidesOnDate=[]
    db.session.execute('''PREPARE myRides (varchar, date) AS SELECT * FROM Ride WHERE driver_netid = $1 AND date= $2;''')
    myRidesOnDate.extend(db.session.execute('EXECUTE myRides(:driver_netid, :date)', {"driver_netid":session['netid'], "date":date}))
    db.session.execute('DEALLOCATE myRides')
    return myRidesOnDate != []
    
#returns true if the user already has a reservation on that date (can't book another)
def check_revs_on_date(date):
    myRevsOnDate=[]
    db.session.execute('''PREPARE myRevs (varchar, date) AS SELECT * FROM Reserve rev WHERE rev.rider_netid = $1\
        AND EXISTS (SELECT * FROM Ride r WHERE r.ride_no=rev.ride_no and r.date=$2);''')
    myRevsOnDate.extend(db.session.execute('EXECUTE myRevs(:driver_netid, :date)', {"driver_netid":session['netid'], "date":date}))
    db.session.execute('DEALLOCATE myRevs')
    return myRevsOnDate != []

#updates the seats available in  the ride and creates the reservation
def book_ride(ride, spots_needed, rideNo, notes):
    #update seats available in ride
    ride.seats_available = ride.seats_available - spots_needed
    db.session.commit()

    #create entry in Reserve table
    newEntry = models.Reserve(rider_netid = session['netid'], ride_no = rideNo, seats_needed = spots_needed, note = notes)
    db.session.add(newEntry)
    db.session.commit()
    flash("Successfully booked. You can find the driver's netid on your account page. \
        It is recommended you reach out to your driver for more information about exact pick up time/ location.")




