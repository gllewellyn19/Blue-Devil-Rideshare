from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template
import datetime 
from datetime import date

import forms
import models

def get_info():
    form = forms.RideNumberFactory()
    validRideNo = False
    reservations = None
    rideNumber = None
    
    if form.validate_on_submit():
        rideNumber = request.form['ride_no']
        ride = db.session.query(models.Ride).filter(models.Ride.ride_no == rideNumber).filter(models.Ride.driver_netid == session['netid']).first()
        if (ride == None):
            flash("Ride not found.")
            return redirect(url_for('rides.account_main'))
        else: 
            validRideNo = True
            reservations = db.session.query(models.Reserve).filter(models.Reserve.ride_no == ride.ride_no)
            if reservations.first() == None:
                reservations = None

    return render_template('accountPages/riders-netids.html', form=form, validRideNo = validRideNo, reservations=reservations, rideNumber=rideNumber)