from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for, render_template

import forms
import models

def account_info():

    """db.session.execute('''PREPARE NewLoc (varchar) AS INSERT INTO Driving_locations VALUES ($1);''')
    newLoc = db.session.execute('EXECUTE NewLoc(:loc)',{"loc":"('Arlington, TX', 'Arlington, TX')"})
    db.session.commit()
    db.session.execute('DEALLOCATE NewLoc')

    locations=db.session.query(models.Driving_locations).all()
    locationsReturn=[]
    for ele in locations:
        locationsReturn.append(ele)"""
    user = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).first()
    driver = db.session.query(models.Driver).filter(models.Driver.netid == session['netid']).first()
    today = datetime.date.today()

    ridesListed,rideToday=get_rides_listed(today)
    reservations,revToday=get_revs_listed(today)

    return render_template('accountPages/account.html', user=user, driver=driver, ridesListed=ridesListed,\
        reservations=reservations, rideToday=rideToday, revToday=revToday)

#returns the upcoming rides in the ridesListed variable and if there is a ride on today's date it puts it in the rideToday variable
#and removes it from the list of future rides
def get_rides_listed(today):
    db.session.execute('''PREPARE RidesPosted (varchar, date) AS SELECT * FROM Ride WHERE driver_netid = $1\
        AND date >= $2 ORDER BY date ASC;''')
    ridesListed = []
    ridesListed.extend(db.session.execute('EXECUTE RidesPosted(:driver_netid, :date)', {"driver_netid":session['netid'],\
        "date":today}))

    #find if a ride is today from the rides listed-> it will be the first item in the list since sorted by date
    rideToday = None
    if ridesListed != []:
        firstRide = ridesListed[0]
        if firstRide.date == today:
            rideToday = ridesListed.pop(0) #remove today's ride from the list of rides
    db.session.execute('DEALLOCATE RidesPosted')
    return ridesListed,rideToday

#returns the upcoming reservations in the reservations variable and if there is a reservation on today's date,
#it puts it in the revToday variable and removes it from the list
def get_revs_listed(today):
    db.session.execute('''PREPARE Reservations (varchar, date) AS SELECT * FROM Reserve R1, Ride R2\
        WHERE R1.rider_netid = $1 AND R1.ride_no = R2.ride_no AND date >= $2 ORDER BY date ASC;''')

    reservations = []
    reservations.extend(db.session.execute('EXECUTE Reservations(:driver_netid, :date)', {"driver_netid":session['netid'],\
        "date":today}))

    #find if a reservation is today from reservations-> it will be the first item in the list since sorted by date
    revToday = None
    if reservations != []:
        firstRev = reservations[0]
        if firstRev.date == today:
            revToday = reservations.pop(0) #remove today's reservation from the list of reservations
    db.session.execute('DEALLOCATE Reservations')
    return reservations,revToday

    

