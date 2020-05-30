from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for, render_template

import forms
import models


def reserve_rides(rideNo, spotsNeeded):
    reserveForm = forms.ReserveRideFormFactory()
    searchForm = forms.SearchFormFactory()
    edit_ride = db.session.query(models.Ride).filter(models.Ride.ride_no == rideNo).first()

    if reserveForm.validate_on_submit():
        notes = request.form['notes']

        #dont allow to book ride if requesting more spots than there is available (would be because someone else just reserved the ride- this should never really happen)
        if spotsNeeded > edit_ride.seats_available:
            flash("Not enough spots in this ride as the number of spots available changed since your request.")
            return redirect(url_for('rides.find_rides_main')) #NOTE: doesn't work right now
        
        #don't allow the user to reserve the ride if they are driving a ride on that date
        myRidesOnDate=[]
        db.session.execute('''PREPARE myRides (varchar, date) AS SELECT * FROM Ride WHERE driver_netid = $1 AND date= $2;''')
        myRidesOnDate.extend(db.session.execute('EXECUTE myRides(:driver_netid, :date)', {"driver_netid":session['netid'], "date":edit_ride.date}))
        db.session.execute('DEALLOCATE myRides')
        if myRidesOnDate != []:
            flash("You are already driving a ride on this day and can't reserve a ride.")
            return redirect(url_for('rides.find_rides_main'))

        #don't allow the user to reserve the ride if they have already reserved a ride on that date
        myRevsOnDate=[]
        db.session.execute('''PREPARE myRevs (varchar, date) AS SELECT * FROM Reserve rev WHERE rev.rider_netid = $1\
            AND EXISTS (SELECT * FROM Ride r WHERE r.ride_no=rev.ride_no and r.date=$2);''')
        myRevsOnDate.extend(db.session.execute('EXECUTE myRevs(:driver_netid, :date)', {"driver_netid":session['netid'], "date":edit_ride.date}))
        db.session.execute('DEALLOCATE myRevs')
        if myRevsOnDate != []:
            flash("You have already reserved a ride on this day and can't reserve another ride.")
            return redirect(url_for('rides.find_rides_main'))


        #update seats available in ride
        edit_ride.seats_available = edit_ride.seats_available - spotsNeeded
        db.session.commit()

        #create entry in Reserve table
        newEntry = models.Reserve(rider_netid = session['netid'], ride_no = rideNo, seats_needed = spotsNeeded, note = notes)
        db.session.add(newEntry)
        db.session.commit()
        flash("Successfully booked. You can find the driver's netid on your account page. \
            It is recommended you reach out to your driver for more information about pick up.")
        return redirect(url_for('rides.find_rides_main'))

    return render_template('reserve-rides.html', searchForm=searchForm, reserveForm=reserveForm, ride=edit_ride, spotsNeeded=spotsNeeded)