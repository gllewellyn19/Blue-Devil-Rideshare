from sqlalchemy import sql, orm, ForeignKey
from database import db 

class Rideshare_user(db.Model):
    """
    All users that signed up for blue devil rideshare
    """
    __tablename__ = 'rideshare_user' 
    netid = db.Column('netid', db.String(7), primary_key=True)
    name = db.Column('name', db.String(50))
    duke_email = db.Column('duke_email', db.String(40)) 
    phone_number = db.Column('phone_number', db.Integer())
    affiliation = db.Column('affiliation', db.String(20)) 
    password = db.Column('password', db.String(100))

class Driver(db.Model):
    """
    Model for all users that registered as drivers  
    """
    __tablename__ = 'driver'
    netid = db.Column('netid', db.String(7), db.ForeignKey('rideshare_user.netid'), primary_key=True)
    license_no = db.Column('license_no', db.String(20))
    license_plate_no = db.Column('license_plate_no', db.String(10))
    plate_state = db.Column('plate_state', db.String(4))

class Ride(db.Model):
    """
    Model for the rides drivers have listed
    """
    __tablename__= 'ride'
    ride_no = db.Column('ride_no', db.Integer(), primary_key = True)
    origin = db.Column('origin', db.String(50))
    destination = db.Column('destination', db.String(50))
    driver_netid = db.Column('driver_netid', db.String(7), db.ForeignKey('driver.netid'))
    date = db.Column('date', db.Date())
    earliest_departure = db.Column('earliest_departure', db.Time())
    latest_departure = db.Column('latest_departure', db.Time())
    seats_available = db.Column('seats_available', db.Integer())
    max_seats_available= db.Column('max_seats_available', db.Integer())
    gas_price = db.Column('gas_price', db.Float())
    comments = db.Column('comments', db.String(200))

class Reserve(db.Model):
    """
    Keeps track of reservations
    """
    __tablename__= 'reserve'
    ride_no = db.Column('ride_no', db.Integer(), db.ForeignKey('ride.ride_no'), primary_key=True)
    rider_netid = db.Column('rider_netid', db.String(7), db.ForeignKey('rideshare_user.netid'), primary_key=True)
    seats_needed = db.Column('seats_needed', db.Integer())
    note = db.Column('note', db.String(200)) 

class Driving_locations(db.Model):
    """
    Used by forms page for the select fields for destination and orig
    """
    __tablename__= 'driving_locations'
    location = db.Column('location', db.String(100), primary_key=True)

class Plate_states(db.Model):
    """
    Used by the forms page for the select field for plate state
    """
    __tablename__= 'plate_states'
    state = db.Column('state', db.String(10), primary_key=True)