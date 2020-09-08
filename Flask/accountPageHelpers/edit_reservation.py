from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template
import datetime 
from datetime import date

import forms
import models

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def edit():
    """
    Allows the user to edit or delete a reservation
    """
    user = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).first()
    form = forms.EditReservationFactory()
    reservation = None
    rideNumber = request.args.get('rideNo')
    userHasRev=check_user_has_rev(rideNumber)

    #check if user has this reservation before proceeding
    if userHasRev:
        if form.validate_on_submit():
            cancel,newSpots,comments=extract_info(form)
            ride = db.session.query(models.Ride).filter(models.Ride.ride_no == rideNumber).first()
            reservation = db.session.query(models.Reserve).filter(models.Reserve.ride_no == rideNumber)\
                .filter(models.Reserve.rider_netid==session['netid']).first()

            if cancel == "Yes":
                newSpots = cancel_reservation(reservation)
                email_driver_cancellation(user, ride, reservation)

            else:
                updatedSpots = int(request.form['spots_needed'])
                #only update spots if enough room in the ride
                if valid_new_rev(reservation, ride, updatedSpots):
                    newSpots = update_reservation(reservation, updatedSpots, comments)
                else:
                    return render_template('accountPages/edit-reservation.html', reservation=reservation, ride=ride, form=form)
                
            #update the ride (subtracts the old seats needed if deleting reservation)
            ride.seats_available = ride.seats_available - newSpots
            db.session.commit()
            
            return redirect(url_for('rides.account_main'))
    
    return render_template('accountPages/edit-reservation.html', user=user, form=form, reservation=reservation, userHasRev=userHasRev)

def check_user_has_rev(rideNumber):
    """
    Double check the current user has the given reservation (preventing malicious input from people changing URLs)
    Return true if the current user has the reservation
    """
    #means the user isn't logged in and should not be able to perform this function
    if session['netid']==None:
        return False

    #check if they have the reservation from the ride number given
    db.session.execute('''PREPARE Reservation (integer, varchar) AS SELECT * FROM Reserve WHERE ride_no = $1 AND rider_netid = $2;''')
    reservation=[]
    reservation.extend(db.session.execute('EXECUTE Reservation(:ride_no, :netid)', {"ride_no":rideNumber, "netid":session['netid']}))
    db.session.execute('DEALLOCATE Reservation')
    return reservation != []

def extract_info(form):
    """
    Extracts information from the form and defaults new spots to 0
    """
    cancel = request.form['cancel']
    comments = request.form['comments']
    newSpots = 0

    return cancel,newSpots,comments

def cancel_reservation(reservation):
    """
    Deletes the reservation and returns the number of spots it needed as a negative number for updating the ride
    """
    newSpots = reservation.seats_needed*-1
    db.session.delete(reservation)
    db.session.commit()
    flash("Reservation cancelled.")
    return newSpots

def email_driver_cancellation(user, ride, reservation):
    print(user.name)
    print(user.netid)
    print(ride.ride_no)
    message = Mail(
    from_email='bluedevilrideshare@gmail.com',
    to_emails = ride.driver_netid + '@duke.edu',
    canceller_name = user.name,
    canceller_netid = user.netid,
    cancelled_ride_no = ride.ride_no,
    subject='A rider just cancelled their reservation',
    html_content='<p>Hello,<br><br>Rider {} ({}) has cancelled their reservation for your ride no. {}.<br><br>Thank you for being a driver for Blue Devil Rideshare,<br><br>-The Blue Devil Rideshare Team</p>'.format(canceller_name, canceller_netid, cancelled_ride_no))
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

def update_reservation(reservation, updatedSpots, comments):
    """
    Update the reservation with the new spots needed 
    """
    newSpots = updatedSpots - reservation.seats_needed
    reservation.seats_needed = updatedSpots
    reservation.note=comments
    db.session.commit()
    flash("Reservation updated.")
    return newSpots

def valid_new_rev(reservation, ride, updatedSpots):
    """
    Checks to see if enough spots in the ride for the new reservation
    """
    if updatedSpots > ride.seats_available:
        flash("Not enough room in the ride for spots needed. Reservation not updated.")
        return False
    else:
        return True

    