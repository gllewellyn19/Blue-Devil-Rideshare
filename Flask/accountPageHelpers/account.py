from database import db
from flask import session
import datetime 
from datetime import date

import forms
import models

def account():
    #account prepared statements to generate the upcoming rides and reservations of the user
    db.session.execute('''PREPARE RidesPosted (varchar, date) AS SELECT * FROM Ride WHERE driver_netid = $1 AND date >= $2 ORDER BY date ASC;''')
    db.session.execute('''PREPARE Reservations (varchar, date) AS SELECT * FROM Reserve R1, Ride R2 WHERE R1.rider_netid = $1 AND R1.ride_no = R2.ride_no\
        AND date >= $2 ORDER BY date ASC;''')

    user = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).first()
    driver = db.session.query(models.Driver).filter(models.Driver.netid == session['netid']).first()
    today = datetime.date.today()

    ridesListed = []
    ridesListed.extend(db.session.execute('EXECUTE RidesPosted(:driver_netid, :date)', {"driver_netid":session['netid'], "date":today}))

    #find any rides that are today from the rides listed-> they will be the first item in the list
    rideToday = None
    if ridesListed != []:
        firstRide = ridesListed[0]
        if firstRide.date == today:
            rideToday = ridesListed.pop(0) #remove today's ride from the list of rides
    
    reservations = []
    reservations.extend(db.session.execute('EXECUTE Reservations(:driver_netid, :date)', {"driver_netid":session['netid'], "date":today}))

    #find any reservations that are today from reservations-> they will be the first item in the list
    revToday = None
    if reservations != []:
        firstRev = reservations[0]
        if firstRev.date == today:
            revToday = reservations.pop(0) #remove today's reservation from the list of reservations

    db.session.execute('DEALLOCATE RidesPosted')
    db.session.execute('DEALLOCATE Reservations')
    return user,driver,ridesListed,reservations,rideToday,revToday