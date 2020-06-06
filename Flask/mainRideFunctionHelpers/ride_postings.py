from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template

import forms
import models

def list_ride():
    listForm = forms.ListRideFormFactory()
    driver = models.Driver.query.filter_by(netid=session['netid']).first() 
    
    if listForm.validate_on_submit():
        destination,origin_city,date,earliest_departure,latest_departure,seats_available,gas_price,comments = extract_info(listForm)
        
        if check_rides_on_date(date):
            flash("You are already driving a ride on this day and can't list another ride.")
            return redirect(url_for('rides.list_rides_main'))
        
        if check_revs_on_date(date):
            flash("You have already reserved a ride on this day and can't list a ride.")
            return redirect(url_for('rides.list_rides_main'))

        create_ride(destination,origin_city, date, earliest_departure, latest_departure, seats_available, gas_price, comments, driver.netid) 
    return render_template('basicRidePages/list-rides.html', form=listForm)
    

#extracts all the information from the form
def extract_info(listForm):
    destination = request.form['destination']
    origin_city = request.form['origin_city']
    date = request.form['date']
    earliest_departure = request.form['earliest_departure']
    latest_departure = request.form['latest_departure']
    seats_available = request.form['seats_available']
    gas_price = request.form['gas_price']
    if gas_price == '':
        gas_price = None
    comments = request.form['comments']
    if comments=='':
        comments = None
    return destination,origin_city,date,earliest_departure,latest_departure,seats_available,gas_price,comments


#returns true if the driver is alredy driving a ride on the given date which means they can't drive another
def check_rides_on_date(date):
    ridesOnDate=[]
    db.session.execute('''PREPARE ridesOnDate (varchar, date) AS SELECT * FROM Ride WHERE driver_netid = $1 AND date= $2;''')
    ridesOnDate.extend(db.session.execute('EXECUTE ridesOnDate(:driver_netid, :date)', {"driver_netid":session['netid'], "date":date}))
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

#creates the ride and inserts it into the database 
def create_ride(destination,origin_city, date, earliest_departure, latest_departure, seats_available, gas_price, comments, driver_netid):
    db.session.execute('''PREPARE listRide (varchar, varchar, varchar, date, time, time, integer, float, varchar)\
        AS INSERT INTO Ride VALUES (DEFAULT, $1, $2, $3, $4, $5, $6, $7, $8, $9);''')
    newride = db.session.execute('EXECUTE listRide(:origin_city, :destination, :driver_netid, :date, :earliest_departure, :latest_departure, :seats_available,\
            :gas_price, :comments)', {"origin_city":origin_city, "destination":destination, "driver_netid":driver_netid, "date":date,\
            "earliest_departure":earliest_departure, "latest_departure":latest_departure, "seats_available":seats_available, "gas_price":gas_price, "comments":comments})
    db.session.commit()
    db.session.execute('DEALLOCATE listRide')
    flash("Ride successfully listed.")