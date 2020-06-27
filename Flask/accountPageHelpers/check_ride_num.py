from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template
import datetime 
from datetime import date

import forms
import models

def verify():
    formRideNo = forms.RideNumberFactory()
    typeRide = request.args.get('type')
    if formRideNo.validate_on_submit():
        rideNo = request.form['ride_no'] 

        #check to see if valid number based on ride type and if valid call correct template
        if typeRide=='rev':
            rev, ride=check_valid_rev(rideNo)
            #if rev is none then user didn't enter valid ride number
            if not rev: 
                return redirect(url_for('rides.account_main'))
            else:
                return render_template('accountPages/edit-reservation.html', reservation=rev,ride=ride, form=forms.EditReservationFactory(),\
                    userHasRev=True)
        #means the user is trying to edit a ride or get information about the riders of their ride
        if typeRide=='edit_ride' or typeRide=='rider_info_ride':
            ride=check_valid_ride(rideNo)
            #if ride is none user didn't enter valid ride number
            if not ride:
                return redirect(url_for('rides.account_main'))
            elif typeRide=='edit_ride':
                return redirect(url_for('rides.edit_ride_main', rideNo=ride.ride_no)) 
            else:
                return redirect(url_for('rides.riders_netids_main', rideNo=ride.ride_no)) 

    return render_template('accountPages/verify-ride-number.html', typeRide=typeRide, form=formRideNo)

#checks to see if the ride number entered is a ride and if the user has a reservation with that ride
#returns None for reservation if not 
def check_valid_rev(rideNo):
    reservation=db.session.query(models.Reserve).filter(models.Reserve.ride_no==rideNo).filter(models.Reserve.rider_netid==session['netid']).first()
    ride=db.session.query(models.Ride).filter(models.Ride.ride_no==rideNo).first()
    if reservation == None:
        flash("Reservation not found.")
        return None, None
    elif ride.date < datetime.date.today():
        flash("Can only edit reservations that are today or in the future")
        return None, None
    else:
        return reservation, ride

#check to see if the user posted the ride for the given ride number
def check_valid_ride(rideNo):
    ride=db.session.query(models.Ride).filter(models.Ride.ride_no==rideNo).filter(models.Ride.driver_netid==session['netid']).first()
    if ride == None:
        flash("Ride not found.")
        return None
    elif ride.date < datetime.date.today():
        flash("Can only edit rides that are today or in the future")
        return None
    else:
        return ride

