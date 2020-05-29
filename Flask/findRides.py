from database import db
import datetime 
from datetime import date
from flask import Flask, request, session, flash, redirect, url_for

import forms
import models

def find_rides():
    searchForm = forms.SearchFormFactory()
    results = []
    reserveForm = forms.ReserveRideFormFactory()
    spotsNeeded=0 #will always change once form is submitted

    if searchForm.validate_on_submit():
        #prepared statements to search for rides with destination specific or just search all
        db.session.execute('''PREPARE SearchAll (varchar, date, integer, varchar) AS SELECT * FROM Ride r WHERE r.origin = $1\
            AND r.date = $2 and r.seats_available >= $3 and r.driver_netid!=$4\
            AND NOT EXISTS (SELECT * FROM Reserve rev WHERE rev.ride_no=r.ride_no AND rev.rider_netid=$4);''') 
        db.session.execute('''PREPARE Search (varchar, varchar, date, integer, varchar) AS SELECT * FROM Ride r\
            WHERE r.origin = $1 AND r.destination = $2 AND r.date = $3 and r.seats_available >= $4 and r.driver_netid!=$5\
            AND NOT EXISTS (SELECT * FROM Reserve rev WHERE rev.ride_no=r.ride_no AND rev.rider_netid=$5);''')
        origin_city = request.form['origin_city']
        destination = request.form['destination']
        date = request.form['date']
        spots_needed = request.form['spots_needed']
        spotsNeeded=spots_needed

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

    return spotsNeeded,searchForm,reserveForm,results