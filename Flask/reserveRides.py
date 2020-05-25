from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for

import forms
import models


def reserve_rides(rideNo, spotsNeeded):
    reserveForm = forms.ReserveRideFormFactory()
    searchForm = forms.SearchFormFactory()
    edit_ride = db.session.query(models.Ride).filter(models.Ride.ride_no == rideNo).first()

    if reserveForm.validate_on_submit():
        print("reserve form valid and submit")
        notes = request.form['notes']

        #dont allow to book ride if requesting more spots than there is available (would be because someone else just reserved the ride)
        #DO: make this a validator
        if spotsNeeded > edit_ride.seats_available:
            flash("Not enough spots in this ride as the number of spots available changed since your request.")
            return redirect(url_for('rides.find_rides_main'))

        #update seats available in ride
        edit_ride.seats_available = edit_ride.seats_available - spotsNeeded
        db.session.commit()

        #create entry in Reserve
        newEntry = models.Reserve(rider_netid = session['netid'], ride_no = rideNo, seats_needed = spotsNeeded, note = notes)
        db.session.add(newEntry)
        db.session.commit()
        flash("Successfully booked.")
        return redirect(url_for('rides.find_rides_main'))

    print("end of find rides function")
    return edit_ride,searchForm,reserveForm