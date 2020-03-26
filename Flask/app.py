
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from sqlalchemy import distinct
from datetime import date

app = Flask(__name__)
app.secret_key = 's3cr3t' #change this?
app.config.from_object('config')
db = SQLAlchemy(app, session_options={'autocommit': False})
net = "NETID"

import forms
import models

@app.route('/')
def home_page():
    return render_template('home.html')# are going to have to set some values here equal to something like in beers- to return values?

@app.route('/find-rides', methods=('GET', 'POST'))
def find_rides():
    form = forms.SearchFormFactory()

    if 'logged_in' not in session:
        if session['logged_in']==False:
            flash("You are not logged in. Redirecting you to log in.")
            return redirect(url_for('log_in'))

    if 'logged_in' in session and session['logged_in']==False:
        flash("You are not logged in. Redirecting you to log in.")
        return redirect(url_for('log_in'))     

    else:
        print("errors: ", form.errors)

        if form.is_submitted():
            print("submitted")
            origin_city = request.form['origin_city']
            destination = request.form['destination']
            date = request.form['date']
            spots_needed = request.form['spots_needed']

            if destination == "Search All":
                print("search all")
                results = db.session.query(models.Ride) \
                    .filter(models.Ride.origin == origin_city) \
                    .filter(models.Ride.date == date) \
                    .filter(models.Ride.seats_available <= spots_needed).all()

            else:
                print("not search all")
                results = db.session.query(models.Ride) \
                    .filter(models.Ride.origin == origin_city) \
                    .filter(models.Ride.destination == destination) \
                    .filter(models.Ride.date == date) \
                    .filter(models.Ride.seats_available <= spots_needed).all()
            results = [x.__dict__ for x in results]
            return render_template('find-rides.html', form=form, results = results)

    return render_template('find-rides.html', form=form)

@app.route('/list-rides', methods=['GET','POST'])
def list_rides():
    form = forms.ListRideFormFactory()
    global net
    driver = models.Driver.query.filter_by(netid=net).first()
    print(net)
    if 'logged_in' in session and not driver:
        if session['logged_in']:
            flash("You are signed in but not yet a driver. Redirecting you to driver registration.") #These flash messages aren't displaying on the site
            return redirect(url_for('register_driver', form=forms.RegisterDriverFormFactory()))
    if 'logged_in' not in session:
        if session['logged_in']==False:
            flash("You are not logged in. Redirecting you to log in.")
            return redirect(url_for('log_in'))
    if 'logged_in' in session and session['logged_in']==False:
        flash("You are not logged in. Redirecting you to log in.")
        return redirect(url_for('log_in'))     
    else:
        print(form.errors)

        if form.is_submitted():
            print("submitted")

        if form.validate():
            print("valid")
        

        print(form.errors)
        if form.validate_on_submit():
            driver_netid = request.form['driver_netid']
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

            newride = models.Ride(driver_netid=driver_netid, destination=destination, origin=origin_city, date=date, earliest_time=earliest_departure, latest_time=latest_departure, seats_available=seats_available, gas_price=gas_price, comments=comments)
            db.session.add(newride)
            db.session.commit()

            return redirect(url_for('home_page'))
    return render_template('list-rides.html', form=form)

@app.route('/sign-up', methods=['GET','POST'])
def sign_up():
    form = forms.RegisterFormFactory()
    global net
    driver = models.Driver.query.filter_by(netid=net).first()
    print(net)
    if 'logged_in' in session and not driver:
        if session['logged_in'] == True:
            flash("You are signed in but not yet a driver. Redirecting you to driver registration.") #These flash messages aren't displaying on the site
            return redirect(url_for('register_driver', form=forms.RegisterDriverFormFactory()))
    if 'logged_in' in session and driver:
        if session['logged_in']:
            flash("You are signed in and already registered as a driver. Redirecting you to list a ride.")
            return redirect(url_for('list_rides'))
    else:
        
        #print(form.errors)

        #if form.is_submitted():
            #print("submitted")

        #if form.validate():
            #print("valid")

        #print(form.errors)
        if form.validate_on_submit():
            netid = request.form['netid']
            name = request.form['name']
            duke_email = request.form['duke_email']
            phone_number = request.form['phone_number']
            password = request.form['password']
            affiliation = request.form['affiliation_sel']
            school = request.form['school']

            register = models.Rideshare_user(netid=netid, name=name, duke_email=duke_email, phone_number=phone_number, password=password, affiliation=affiliation, school=school)
            db.session.add(register)
            db.session.commit()

            return redirect(url_for('log_in'))
        return render_template('sign-up.html', form=form)

@app.route('/register-driver', methods=['GET','POST'])
def register_driver():
    form = forms.RegisterDriverFormFactory()
    global net
    driver = models.Driver.query.filter_by(netid=net).first()
    if 'logged_in' in session and driver:
        if session['logged_in']:
            flash("You are already a driver. Redirecting you to list a ride.")
        return redirect(url_for('list_rides'))
    print(form.errors)

    if form.is_submitted():
        print("submitted")

    if form.validate():
        print("valid")

    print(form.errors)
    if form.validate_on_submit():
        netid = net
        license_no = request.form['license_no']
        license_plate_no = request.form['license_plate_no']
        plate_state = request.form['plate_state']
            
        register = models.Driver(netid=netid, license_no=license_no, license_plate_no=license_plate_no, plate_state=plate_state)
        db.session.add(register)
        db.session.commit()
        return redirect(url_for('list_rides'))
    return render_template('register-driver.html', form=form)
    

@app.route('/log-in', methods=['GET','POST'])
def log_in():
    error = None
    if request.method == 'POST':
        netid = request.form.get('netid')
        password = request.form.get('password')
        user = models.Rideshare_user.query.filter_by(netid=netid).first()
        if not user or not (user.password==password):
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            global net
            net = netid
            print(net)
            return redirect(url_for('home_page'))
    return render_template('log-in.html', error=error)

@app.route("/logout")
def log_out():
    session['logged_in'] = False
    global net
    net = "NETID"
    print(net)
    return home_page()

@app.route('/account', methods=('GET', 'POST'))
def account():
    #should have edit form in here
    #NOTE: this will give an error if you are already logged in and try to do this- somehow we need to get the netid if you are already logged in
    user = models.Rideshare_user.query.filter_by(netid=net).first()
    ridesListed = models.Ride.query.filter_by(driver_netid=net)
    ridesReserved = models.Reserve.query.filter_by(rider_netid=net)
    return render_template('account.html', user=user, ridesListed=ridesListed, ridesReserved=ridesReserved)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug = True)
