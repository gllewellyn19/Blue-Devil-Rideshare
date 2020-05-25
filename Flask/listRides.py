from database import db
from flask import Flask, request, session, flash, redirect, url_for

import forms
import models

def list_rides(form):
    driver = models.Driver.query.filter_by(netid=session['netid']).first() 
    
    if form.validate_on_submit():
        
        driver_netid = session['netid']
        destination = request.form['destination']
        origin_city = request.form['origin_city']
        date = request.form['date']
        
        myRides=[]
        db.session.execute('''PREPARE myRides (varchar, date) AS SELECT * FROM Ride WHERE driver_netid = $1 AND date= $2;''')
        myRides.extend(db.session.execute('EXECUTE myRides(:driver_netid, :date)', {"driver_netid":driver_netid, "date":date}))
        db.session.execute('DEALLOCATE myRides')
        if myRides != []:
            flash("You are already driving a ride on this day")
            return redirect(url_for('rides.list_rides_main'))

        myRevs=[]
        db.session.execute('''PREPARE myRevs (varchar, date) AS SELECT * FROM Reserve rev WHERE rev.rider_netid = $1\
            AND EXISTS (SELECT * FROM Ride r WHERE r.ride_no=rev.ride_no and r.date=$2);''')
        myRevs.extend(db.session.execute('EXECUTE myRevs(:driver_netid, :date)', {"driver_netid":driver_netid, "date":date}))
        db.session.execute('DEALLOCATE myRevs')
        if myRevs != []:
            flash("You have already reserved a ride on this day")
            return redirect(url_for('rides.list_rides_main'))

        earliest_departure = request.form['earliest_departure']
        latest_departure = request.form['latest_departure']
        seats_available = request.form['seats_available']
        gas_price = request.form['gas_price']
        if gas_price == '':
            gas_price = None
        comments = request.form['comments']
        if comments=='':
            comments = None
        session['driver'] = True # NEED THIS?
        db.session.execute('''PREPARE List (varchar, varchar, varchar, date, time, time, integer, float, varchar)\
        AS INSERT INTO Ride VALUES (DEFAULT, $1, $2, $3, $4, $5, $6, $7, $8, $9);''')
        newride = db.session.execute('EXECUTE List(:origin_city, :destination, :driver_netid, :date, :earliest_departure, :latest_departure, :seats_available,\
            :gas_price, :comments)', {"origin_city":origin_city, "destination":destination, "driver_netid":driver_netid, "date":date,\
            "earliest_departure":earliest_departure, "latest_departure":latest_departure, "seats_available":seats_available, "gas_price":gas_price, "comments":comments})
        db.session.commit()
        db.session.execute('DEALLOCATE List')
        flash("Ride successfully listed.")
        return redirect(url_for('rides.home_page'))