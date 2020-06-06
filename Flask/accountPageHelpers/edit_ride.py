from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for, render_template

import forms
import models

def edit():
    #NOTE: edit seats available!! (when update data)
    editRideForm=forms.EditRideFactory()
    rideNo=request.args.get('rideNo')
    ride=set_defaults(rideNo, editRideForm)

    if editRideForm.validate_on_submit():
        cancel = request.form['cancel']

        if cancel == "Yes":
            delete_ride(ride)
        else:
            #this means the ride failed to update- if it didn't fail then this function updated the ride
            if not update_ride(ride, editRideForm):
                return redirect(url_for('rides.edit_ride_main', rideNo=rideNo))
        return redirect(url_for('rides.account_main'))

    return render_template('accountPages/edit-ride.html', form=editRideForm, ride=ride)

#sets the defaults for the ride form
def set_defaults(rideNo, editRideForm):
    ride=db.session.query(models.Ride).filter(models.Ride.ride_no == rideNo).first()
    editRideForm.earliest_departure.data=ride.earliest_time
    editRideForm.latest_departure.data=ride.latest_time
    editRideForm.date.data=ride.date
    return ride

#deletes the ride and all reservations for the ride
def delete_ride(ride):
    reservationsToDelete = db.session.query(models.Reserve).filter(models.Reserve.ride_no == ride.ride_no)
    for reservation in reservationsToDelete:
        db.session.delete(reservation)
        db.session.commit()
    db.session.delete(ride)
    db.session.commit()
    flash("Ride cancelled.")

#updates the ride after making sure the date and times are valid (returns false if they aren't)
def update_ride(ride, form):
    newdate=request.form['date']
    newearliest_departure = request.form['earliest_departure']
    newlatest_departure = request.form['latest_departure']
    if not check_times_valid(newearliest_departure, newlatest_departure) or not check_date_valid(newdate, ride.ride_no):
        return False
    newgas_price = request.form['gas_price']
    newcomments = request.form['comments']

    if newgas_price == '':
        newgas_price = None
    if newcomments=='':
        newcomments = None
            
    ride.gas_price = newgas_price
    ride.comments = newcomments
    ride.earliest_time = newearliest_departure
    ride.latest_time = newlatest_departure
    ride.date = newdate
    db.session.commit()
    flash("Ride updated.")
    return True

#checks to make sure the earliest departure is before the latest departure (returns true if valid)
def check_times_valid(earliest_departure, latest_departure):
    if earliest_departure > latest_departure:
        flash("Earliest departure must be before latest departure")
        return False
    return True

#checks to make sure that the date is after today's date and driver doesn't have a ride on that day (returns true if valid)
def check_date_valid(date, rideNo):
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

#returns true if the driver is alredy driving a ride on the given date which means they can't drive another
def check_rides_on_date(date, rideNo):
    ridesOnDate=[]
    db.session.execute('''PREPARE ridesOnDate (varchar, date) AS SELECT * FROM Ride WHERE driver_netid = $1 AND date= $2 AND ride_no!=$3;''')
    ridesOnDate.extend(db.session.execute('EXECUTE ridesOnDate(:driver_netid, :date, :ride_no)', {"driver_netid":session['netid'], "date":date, "ride_no":rideNo}))
    db.session.execute('DEALLOCATE ridesOnDate')
    return ridesOnDate!=[]

#returns true if the driver already has a reservation on the given date which means they can't drive a ride too
def check_revs_on_date(date):
    revsOnDate=[]
    db.session.execute('''PREPARE revsOnDate (varchar, date) AS SELECT * FROM Reserve rev WHERE rev.rider_netid = $1\
            AND EXISTS (SELECT * FROM Ride r WHERE r.ride_no=rev.ride_no and r.date=$2);''')
    revsOnDate.extend(db.session.execute('EXECUTE revsOnDate(:driver_netid, :date)', {"driver_netid":session['netid'], "date":date}))
    db.session.execute('DEALLOCATE revsOnDate')
    return revsOnDate!=[]
