from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template
import datetime 
from datetime import date

import forms
import models

def account():
    #account prepared statements
    db.session.execute('''PREPARE RidesPosted (varchar, date) AS SELECT * FROM Ride WHERE driver_netid = $1 AND date >= $2 ORDER BY date ASC;''')
    db.session.execute('''PREPARE Reservations (varchar, date) AS SELECT * FROM Reserve R1, Ride R2 WHERE R1.rider_netid = $1 AND R1.ride_no = R2.ride_no\
        AND date >= $2 ORDER BY date ASC;''')

    user = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).first()
    driver = db.session.query(models.Driver).filter(models.Driver.netid == session['netid']).first()
    today = datetime.date.today()

    print("="*50)
    print(today)

    ridesListed = []
    ridesListed.extend(db.session.execute('EXECUTE RidesPosted(:driver_netid, :date)', {"driver_netid":session['netid'], "date":today}))

    #find any rides that are today from the rides listed-> they will be the last item in the list
    rideToday = None
    if ridesListed != []:
        firstRide = ridesListed[0]
        print(firstRide.date)
        if firstRide.date == today:
            print("in if")
            rideToday = firstRide
            ridesListed.remove(firstRide)
    

    reservations = []
    reservations.extend(db.session.execute('EXECUTE Reservations(:driver_netid, :date)', {"driver_netid":session['netid'], "date":today}))

    #find any rides that are today from the rides listed-> they will be the last item in the list
    revToday = None
    if reservations != []:
        firstRev = reservations[0]
        if firstRev.date == today:
            revToday = firstRev 
            reservations.remove(firstRev)

    db.session.execute('DEALLOCATE RidesPosted')
    db.session.execute('DEALLOCATE Reservations')
    return user,driver,ridesListed,reservations,rideToday,revToday