import datetime 
from datetime import date
from database import db
from flask import session, render_template

def get_prev_revs():
    #use prepared statements to find all of the users reservations in the past
    db.session.execute('''PREPARE PastReservations (varchar, date) AS SELECT * FROM Reserve R1, Ride R2 WHERE R1.rider_netid = $1 AND R1.ride_no = R2.ride_no\
        AND date < $2 ORDER BY date ASC;''')
    past_revs = []
    past_revs.extend(db.session.execute('EXECUTE PastReservations(:driver_netid, :date)', {"driver_netid":session['netid'], "date":datetime.date.today()}))
    db.session.execute('DEALLOCATE PastReservations')
    return render_template('accountPages/past-reservations.html', past_revs=past_revs)