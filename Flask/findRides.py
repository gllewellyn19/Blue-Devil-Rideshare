from database import db
import datetime #remove later
from datetime import date
from flask import Flask, request, session, flash, redirect, url_for

import forms
import models

def find_rides():
    searchForm = forms.SearchFormFactory()
    results = []
    reserveForm = forms.ReserveRideFormFactory()
    spotsNeeded=0 #will always change once form is submitted

    #search prepared statements 
    if searchForm.validate_on_submit():
        db.session.execute('''PREPARE SearchAll (varchar, date, integer, varchar) AS SELECT * FROM Ride WHERE origin = $1
            AND date = $2 and seats_available >= $3 and driver_netid!=$4;''')
        db.session.execute('''PREPARE Search (varchar, varchar, date, integer, varchar) AS SELECT * FROM Ride
            WHERE origin = $1 AND destination = $2 AND date = $3 and seats_available >= $4 and driver_netid!=$5;''')
        origin_city = request.form['origin_city']
        destination = request.form['destination']
        date = request.form['date']
        spots_needed = request.form['spots_needed']
        spotsNeeded=spots_needed

        #change later to validators
        if origin_city == destination:
            flash("Origin and destination cannot be the same.")
            db.session.execute('DEALLOCATE SearchALL')
            db.session.execute('DEALLOCATE Search')
            return None,None,None,None
        if date < str(datetime.date.today()):
            flash("Date entered must be after today's date.")
            db.session.execute('DEALLOCATE SearchALL')
            db.session.execute('DEALLOCATE Search')
            return None,None,None,None

        if destination == "Search All":
            results.extend(db.session.execute('EXECUTE SearchAll(:origin_city, :date, :spots_needed, :driver_netid)',\
                {"origin_city":origin_city, "date":date, "spots_needed":spots_needed, "driver_netid":session['netid']}))
            db.session.execute('DEALLOCATE SearchALL')
            db.session.execute('DEALLOCATE Search')
        else:
            results.extend(db.session.execute('EXECUTE Search(:origin_city, :destination, :date, :spots_needed, :driver_netid)',\
                {"origin_city":origin_city, "destination":destination, "date":date, "spots_needed":spots_needed, "driver_netid":session['netid']}))
            db.session.execute('DEALLOCATE SearchALL')
            db.session.execute('DEALLOCATE Search')

        #NOTE: Danai does this look bad?
        #IMPLEMENT
        resultsToReturn=[]
        for result in results:
            previousReservation = db.session.query(models.Reserve).filter(models.Reserve.ride_no == result.ride_no, models.Reserve.rider_netid == session['netid']).first()
            if previousReservation==None:
                resultsToReturn.append(result)
        


    return spotsNeeded,searchForm,reserveForm,results