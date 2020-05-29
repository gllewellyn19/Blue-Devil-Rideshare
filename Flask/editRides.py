from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for

import forms
import models

def editRidesRideNoCheck(editForm, formRideNo):
    validRideNo = False
    rideToEdit = None
    returnStatement = render_template('edit-list-ride.html', editForm=form, formRideNo=formRideNo, validRideNo = validRideNo, ride=rideToEdit)
    
    if formRideNo.validate_on_submit():
        rideNumber = request.form['ride_no']
        rideToEdit = db.session.query(models.Ride).filter(models.Ride.ride_no == rideNumber).filter(models.Ride.driver_netid == session['netid']).first()
        if (rideToEdit == None):
            flash("Ride not found.")
            returnStatement = redirect(url_for('rides.account'))
            return returnStatement
        else: 
            print(rideToEdit.earliest_time)
            validRideNo = True

    return returnStatement