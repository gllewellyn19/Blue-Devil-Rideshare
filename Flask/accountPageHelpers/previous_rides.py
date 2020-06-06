import datetime 
from datetime import date
from database import db
from flask import session, render_template

def get_prev_rides():
    #use prepared statements to find all of the users rides in the past
    db.session.execute('''PREPARE PastRides (varchar, date) AS SELECT * FROM Ride WHERE driver_netid = $1 AND date < $2 ORDER BY date ASC;''')
    past_rides = []
    past_rides.extend(db.session.execute('EXECUTE PastRides(:driver_netid, :date)', {"driver_netid":session['netid'], "date":datetime.date.today()}))
    db.session.execute('DEALLOCATE PastRides')
    return render_template('accountPages/past-rides.html', past_rides=past_rides)