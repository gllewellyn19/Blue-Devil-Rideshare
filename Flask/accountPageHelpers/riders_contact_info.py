from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template
import datetime 
from datetime import date

import forms
import models

def get_info():
    """
    Gets the contact information for the riders of the ride that the driver is riding
    """
    rideNo=request.args.get('rideNo')
    userDrivingRide=check_user_driving_ride(rideNo)

    db.session.execute('''PREPARE Reservations (integer) AS SELECT * FROM Reserve R, Rideshare_user U WHERE R.ride_no = $1 AND R.rider_netid = U.netid;''')
    reservations = []
    reservations.extend(db.session.execute('EXECUTE Reservations(:ride_no)', {"ride_no":rideNo}))
    db.session.execute('DEALLOCATE Reservations')

    return render_template('accountPages/riders-netids.html', reservations=reservations, rideNo=rideNo, userDrivingRide=userDrivingRide)

def check_user_driving_ride(rideNo):
    """
    Double check the current user is the one driving the ride (preventing malicious input from people changing URLs)
    Return true if the current user is who is driving this ride
    """
    
    #means the user isn't logged in and should not be able to perform this function
    if session['netid']==None:
        return False

    #check if user is driving the ride number given- if not return false
    db.session.execute('''PREPARE Ride (integer, varchar) AS SELECT * FROM Ride WHERE ride_no = $1 AND driver_netid = $2;''')
    ride=[]
    ride.extend(db.session.execute('EXECUTE Ride(:ride_no, :netid)', {"ride_no":rideNo, "netid":session['netid']}))
    db.session.execute('DEALLOCATE Ride')
    return ride != []
