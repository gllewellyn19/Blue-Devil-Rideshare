from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, HiddenField, IntegerField, PasswordField, validators, SubmitField, SelectField, ValidationError, DecimalField, DateTimeField
from wtforms_components import TimeField, DateRange
from wtforms.validators import InputRequired, Length, NumberRange, Regexp, Email, DataRequired, Optional, EqualTo, ValidationError
from wtforms.fields.html5 import DateTimeLocalField, DateField
#from app import db #???
import models
import datetime
from datetime import date
from database import db
from flask import session
import models

def NotEqualTo():
    message = 'Your destination city cannot be the same as your origin.'

    def _NotEqualTo(form, field):
        if field.data == form.origin_city.data:
            raise ValidationError(message)

    return _NotEqualTo

def GreaterThanEarliestDeparture():
    message = 'Your latest departure time must be after your earliest departure time'
    
    def _GreaterThanEarliestDeparture(form, field):
        if field.data < form.earliest_departure.data:
            raise ValidationError(message)
    return _GreaterThanEarliestDeparture

def ConfirmPassEqual():
    message = 'Your confirm password must match your password'

    def _ConfirmPassEqual(form, field):
        if field.data != form.password.data:
            raise ValidationError(message)
    return _ConfirmPassEqual

def CheckIfExistingNetid():
    message = 'An account with this netID already exists. Please log in if this is your netID'

    def _CheckIfExistingNetid(form, field):
        existingUsers = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == field.data)
        if existingUsers.first() != None:
            raise ValidationError(message)
    return _CheckIfExistingNetid

def CorrectPassword():
    message = 'The current password you entered does not match your password'

    def _CorrectPassword(form, field):
        user = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).first()
        print(user)
        if field.data != user.password:
            raise ValidationError(message)
    return _CorrectPassword

def OptionalIfNotDriver():
    message = 'Your license plate number must be between 2 and 10 characters'

    def _OptionalIfNotDriver(form, field):
        if session['driver']==True and (len(field.data)<2 or len(field.data)>10):
            raise ValidationError(message)
    return _OptionalIfNotDriver
 
class RegisterFormFactory(FlaskForm):
    netid = StringField("NetID:", validators = [InputRequired(message='You must enter your NetID'), CheckIfExistingNetid(), Length(min=4, max=7, message='Your NetID must be between 4 and 7 characters')])
    name = StringField("Name:", validators = [InputRequired(message='You must enter your name'), Length(min=5, max=50, message='Your name must be between 5 and 50 characters')])
    duke_email = StringField("Duke Email:", validators = [InputRequired(message='You must enter your Duke email'), Email(message='You must enter a valid email address'),\
        Length(min=10, max=40, message='Your email must be between 10 to 40 characters'), Regexp('^[a-zA-Z0-9]+@duke.edu$', message = 'Please enter a valid Duke email address')])
    phone_number = StringField("Phone Number:", validators = [InputRequired(message='You must enter a valid phone number'), Regexp('^[0-9]', message = 'Please enter only numbers for phone number'), Length(min=10, max=12, message='Your phone number must be between 10 and 12 characters')])
    password = PasswordField("Password:", validators = [InputRequired(message='You must enter a password'),\
        Length(min=5, max=100, message='Your password must be between 5 and 100 characters')])
    confirm_password = PasswordField("Confirm Password:", validators = [InputRequired(message='You must confirm your password'), ConfirmPassEqual()])
    affiliation_sel = SelectField("Affiliation:", validators = [InputRequired(message='You must select your affiliation')],\
        choices = [('Graduate', 'Graduate'), ('Undergraduate', 'Undergraduate')], default='Undergraduate')
    submit = SubmitField("Submit")      

class RegisterDriverFormFactory(FlaskForm):
    license_no = StringField("License Number", validators = [InputRequired(message='You must enter your license number'), Length(min=5, max=20, message='You must enter a license plate number that is between 5 and 20 characters')])
    license_plate_no = StringField("License Plate Number", validators = [InputRequired(message='You must enter your license plate number'), Length(min=2, max=10, message='You must enter a license plate number between 2 and 10 characters')])
    plate_state = SelectField("State", choices = [('AL', 'AL'), ('AK', 'AK'), ('AZ', 'AZ'), ('AR', 'AR'), ('CA', 'CA'), ('CO', 'CO'), ('CT', 'CT'), ('DE', 'DE'), ('FL', 'FL'), ('GA', 'GA'), ('HI', 'HI'), ('ID', 'ID'), ('IL', 'IL'), ('IN', 'IN'), ('IA', 'IA'), ('KS', 'KS'), ('KY', 'KY'), ('LA', 'LA'), ('ME', 'ME'), ('MD', 'MD'), ('MA', 'MA'), ('MI', 'MI'), ('MN', 'MN'), ('MS', 'MS'), ('MO', 'MO'), ('MT', 'MT'), ('NE', 'NE'), ('NV', 'NV'), ('NH', 'NH'), ('NJ', 'NJ'), ('NM', 'NM'), ('NY', 'NY'), ('NC', 'NC'), ('ND', 'ND'), ('OH', 'OH'), ('OK', 'OK'), ('OR', 'OR'), ('PA', 'PA'), ('RI', 'RI'), ('SC', 'SC'), ('SD', 'SD'), ('TN', 'TN'), ('TX', 'TX'), ('UT', 'UT'), ('VT', 'VT'), ('VA', 'VA'), ('WA', 'WA'), ('WV', 'WV'), ('WI', 'WI'), ('WY', 'WY'), ('GU', 'GU'), ('PR', 'PR'), ('VI', 'VI')], default = 'NC')
    submit = SubmitField("Submit") 

class SearchFormFactory(FlaskForm):
    origin_city = SelectField("Origin City:", coerce=str, choices = [('Albuquerque, NM', 'Albuquerque, NM'), ('Arlington, TX', 'Arlington, TX'), ('Asheville, NC', 'Asheville, NC'), ('Aspen, CO', 'Aspen, CO'), ('Atlanta, GA', 'Atlanta, GA'), ('Austin, TX', 'Austin, TX'), ('Baltimore, MD', 'Baltimore, MD'), ('Boca Grande, FL', 'Boca Grande, FL'), ('Boston, MA', 'Boston, MA'), ('Cary, NC', 'Cary, NC'), ('Charlotte, NC', 'Charlotte, NC'), ('Chicago, IL', 'Chicago, IL'), ('Colorado Springs, CO', 'Colorado Springs, CO'), ('Columbus, OH', 'Columbus, OH'), ('Concord, NC', 'Concord, NC'), ('Dallas, TX', 'Dallas, TX'), ('Denver, CO', 'Denver, CO'), ('Detroit, MI', 'Detroit, MI'), ('Durham, NC', 'Durham, NC'), ('El Paso, TX', 'El Paso, TX'), ('Fayetteville, NC', 'Fayetteville, NC'), ('Fort Worth, TX', 'Fort Worth, TX'), ('Fresno, CA', 'Fresno, CA'), ('Greensboro, NC', 'Greensboro, NC'), ('Greenville, NC', 'Greenville, NC'), ('High Point, NC', 'High Point, NC'), ('Houston, TX', 'Houston, TX'), ('Indianapolis, IN', 'Indianapolis, IN'), ('Jacksonville, FL', 'Jacksonville, FL'), ('Kansas City, MO', 'Kansas City, MO'), ('Las Vegas, NV', 'Las Vegas, NV'), ('Long Beach, CA', 'Long Beach, CA'), ('Los Angeles, CA', 'Los Angeles, CA'), ('Louisville, KY', 'Louisville, KY'), ('Memphis, TN', 'Memphis, TN'), ('Mesa, AZ', 'Mesa, AZ'), ('Miami, FL', 'Miami, FL'), ('Milwaukee, WI', 'Milwaukee, WI'), ('Minneapolis, MN', 'Minneapolis, MN'), ('Myrtle Beach, SC', 'Myrtle Beach, SC'), ('Nashville, TN', 'Nashville, TN'), ('New Orleans, LA', 'New Orleans, LA'), ('New York, NY', 'New York, NY'), ('Oakland, CA', 'Oakland, CA'), ('Oklahoma City, OK', 'Oklahoma City, OK'), ('Omaha, NE', 'Omaha, NE'), ('Philadelphia, PA', 'Philadelphia, PA'), ('Phoenix, AZ', 'Phoenix, AZ'), ('Portland, OR', 'Portland, OR'), ('Raleigh, NC', 'Raleigh, NC'), ('Sacramento, CA', 'Sacramento, CA'), ('San Antonio, TX', 'San Antonio, TX'), ('San Diego, CA', 'San Diego, CA'), ('San Francisco, CA', 'San Francisco, CA'), ('San Jose, CA', 'San Jose, CA'), ('Seattle, WA', 'Seattle, WA'), ('Tucson, AZ', 'Tucson, AZ'), ('Tulsa, OK', 'Tulsa, OK'), ('Virginia Beach, VA', 'Virginia Beach, VA'), ('Washington, DC', 'Washington, DC'), ('Wichita, KS', 'Wichita, KS'), ('Wilmington, NC', 'Wilmington, NC'), ('Winston-Salem, NC', 'Winston-Salem, NC')], default = 'Durham, NC')
    destination = SelectField("Destination City:", validators = [NotEqualTo()], choices = [('Search All', 'Search All'), ('Albuquerque, NM', 'Albuquerque, NM'), ('Arlington, TX', 'Arlington, TX'), ('Asheville, NC', 'Asheville, NC'), ('Aspen, CO', 'Aspen, CO'), ('Atlanta, GA', 'Atlanta, GA'), ('Austin, TX', 'Austin, TX'), ('Baltimore, MD', 'Baltimore, MD'), ('Boca Grande, FL', 'Boca Grande, FL'), ('Boston, MA', 'Boston, MA'), ('Cary, NC', 'Cary, NC'), ('Charlotte, NC', 'Charlotte, NC'), ('Chicago, IL', 'Chicago, IL'), ('Colorado Springs, CO', 'Colorado Springs, CO'), ('Columbus, OH', 'Columbus, OH'), ('Concord, NC', 'Concord, NC'), ('Dallas, TX', 'Dallas, TX'), ('Denver, CO', 'Denver, CO'), ('Detroit, MI', 'Detroit, MI'), ('Durham, NC', 'Durham, NC'), ('El Paso, TX', 'El Paso, TX'), ('Fayetteville, NC', 'Fayetteville, NC'), ('Fort Worth, TX', 'Fort Worth, TX'), ('Fresno, CA', 'Fresno, CA'), ('Greensboro, NC', 'Greensboro, NC'), ('Greenville, NC', 'Greenville, NC'), ('High Point, NC', 'High Point, NC'), ('Houston, TX', 'Houston, TX'), ('Indianapolis, IN', 'Indianapolis, IN'), ('Jacksonville, FL', 'Jacksonville, FL'), ('Kansas City, MO', 'Kansas City, MO'), ('Las Vegas, NV', 'Las Vegas, NV'), ('Long Beach, CA', 'Long Beach, CA'), ('Los Angeles, CA', 'Los Angeles, CA'), ('Louisville, KY', 'Louisville, KY'), ('Memphis, TN', 'Memphis, TN'), ('Mesa, AZ', 'Mesa, AZ'), ('Miami, FL', 'Miami, FL'), ('Milwaukee, WI', 'Milwaukee, WI'), ('Minneapolis, MN', 'Minneapolis, MN'), ('Myrtle Beach, SC', 'Myrtle Beach, SC'), ('Nashville, TN', 'Nashville, TN'), ('New Orleans, LA', 'New Orleans, LA'), ('New York, NY', 'New York, NY'), ('Oakland, CA', 'Oakland, CA'), ('Oklahoma City, OK', 'Oklahoma City, OK'), ('Omaha, NE', 'Omaha, NE'), ('Philadelphia, PA', 'Philadelphia, PA'), ('Phoenix, AZ', 'Phoenix, AZ'), ('Portland, OR', 'Portland, OR'), ('Raleigh, NC', 'Raleigh, NC'), ('Sacramento, CA', 'Sacramento, CA'), ('San Antonio, TX', 'San Antonio, TX'), ('San Diego, CA', 'San Diego, CA'), ('San Francisco, CA', 'San Francisco, CA'), ('San Jose, CA', 'San Jose, CA'), ('Seattle, WA', 'Seattle, WA'), ('Tucson, AZ', 'Tucson, AZ'), ('Tulsa, OK', 'Tulsa, OK'), ('Virginia Beach, VA', 'Virginia Beach, VA'), ('Washington, DC', 'Washington, DC'), ('Wichita, KS', 'Wichita, KS'), ('Wilmington, NC', 'Wilmington, NC'), ('Winston-Salem, NC', 'Winston-Salem, NC')])
    date = DateField("Departure Date:", validators=[InputRequired(message='Please enter desired departure date'), DateRange(min = datetime.date.today(),  message="Date must be greater than or equal to "+ str(datetime.date.today()))], format='%Y-%m-%d')
    spots_needed = IntegerField("Spots Needed:", validators=[InputRequired(message='Please enter spots needed')], default=1)
    submit = SubmitField("Search")
                                        
class ListRideFormFactory(FlaskForm):
    #choices=new database table that is destinations and loop through all destinations-- query to database
    origin_city = SelectField("Origin City:", coerce=str, choices = [('Albuquerque, NM', 'Albuquerque, NM'), ('Arlington, TX', 'Arlington, TX'), ('Asheville, NC', 'Asheville, NC'), ('Aspen, CO', 'Aspen, CO'), ('Atlanta, GA', 'Atlanta, GA'), ('Austin, TX', 'Austin, TX'), ('Baltimore, MD', 'Baltimore, MD'), ('Boca Grande, FL', 'Boca Grande, FL'), ('Boston, MA', 'Boston, MA'), ('Cary, NC', 'Cary, NC'), ('Charlotte, NC', 'Charlotte, NC'), ('Chicago, IL', 'Chicago, IL'), ('Colorado Springs, CO', 'Colorado Springs, CO'), ('Columbus, OH', 'Columbus, OH'), ('Concord, NC', 'Concord, NC'), ('Dallas, TX', 'Dallas, TX'), ('Denver, CO', 'Denver, CO'), ('Detroit, MI', 'Detroit, MI'), ('Durham, NC', 'Durham, NC'), ('El Paso, TX', 'El Paso, TX'), ('Fayetteville, NC', 'Fayetteville, NC'), ('Fort Worth, TX', 'Fort Worth, TX'), ('Fresno, CA', 'Fresno, CA'), ('Greensboro, NC', 'Greensboro, NC'), ('Greenville, NC', 'Greenville, NC'), ('High Point, NC', 'High Point, NC'), ('Houston, TX', 'Houston, TX'), ('Indianapolis, IN', 'Indianapolis, IN'), ('Jacksonville, FL', 'Jacksonville, FL'), ('Kansas City, MO', 'Kansas City, MO'), ('Las Vegas, NV', 'Las Vegas, NV'), ('Long Beach, CA', 'Long Beach, CA'), ('Los Angeles, CA', 'Los Angeles, CA'), ('Louisville, KY', 'Louisville, KY'), ('Memphis, TN', 'Memphis, TN'), ('Mesa, AZ', 'Mesa, AZ'), ('Miami, FL', 'Miami, FL'), ('Milwaukee, WI', 'Milwaukee, WI'), ('Minneapolis, MN', 'Minneapolis, MN'), ('Myrtle Beach, SC', 'Myrtle Beach, SC'), ('Nashville, TN', 'Nashville, TN'), ('New Orleans, LA', 'New Orleans, LA'), ('New York, NY', 'New York, NY'), ('Oakland, CA', 'Oakland, CA'), ('Oklahoma City, OK', 'Oklahoma City, OK'), ('Omaha, NE', 'Omaha, NE'), ('Philadelphia, PA', 'Philadelphia, PA'), ('Phoenix, AZ', 'Phoenix, AZ'), ('Portland, OR', 'Portland, OR'), ('Raleigh, NC', 'Raleigh, NC'), ('Sacramento, CA', 'Sacramento, CA'), ('San Antonio, TX', 'San Antonio, TX'), ('San Diego, CA', 'San Diego, CA'), ('San Francisco, CA', 'San Francisco, CA'), ('San Jose, CA', 'San Jose, CA'), ('Seattle, WA', 'Seattle, WA'), ('Tucson, AZ', 'Tucson, AZ'), ('Tulsa, OK', 'Tulsa, OK'), ('Virginia Beach, VA', 'Virginia Beach, VA'), ('Washington, DC', 'Washington, DC'), ('Wichita, KS', 'Wichita, KS'), ('Wilmington, NC', 'Wilmington, NC'), ('Winston-Salem, NC', 'Winston-Salem, NC')], default = 'Durham, NC')
    destination = SelectField("Destination City:", validators = [InputRequired(message='You must select a destination city'), NotEqualTo()], choices = [('Albuquerque, NM', 'Albuquerque, NM'), ('Arlington, TX', 'Arlington, TX'), ('Asheville, NC', 'Asheville, NC'), ('Aspen, CO', 'Aspen, CO'), ('Atlanta, GA', 'Atlanta, GA'), ('Austin, TX', 'Austin, TX'), ('Baltimore, MD', 'Baltimore, MD'), ('Boca Grande, FL', 'Boca Grande, FL'), ('Boston, MA', 'Boston, MA'), ('Cary, NC', 'Cary, NC'), ('Charlotte, NC', 'Charlotte, NC'), ('Chicago, IL', 'Chicago, IL'), ('Colorado Springs, CO', 'Colorado Springs, CO'), ('Columbus, OH', 'Columbus, OH'), ('Concord, NC', 'Concord, NC'), ('Dallas, TX', 'Dallas, TX'), ('Denver, CO', 'Denver, CO'), ('Detroit, MI', 'Detroit, MI'), ('Durham, NC', 'Durham, NC'), ('El Paso, TX', 'El Paso, TX'), ('Fayetteville, NC', 'Fayetteville, NC'), ('Fort Worth, TX', 'Fort Worth, TX'), ('Fresno, CA', 'Fresno, CA'), ('Greensboro, NC', 'Greensboro, NC'), ('Greenville, NC', 'Greenville, NC'), ('High Point, NC', 'High Point, NC'), ('Houston, TX', 'Houston, TX'), ('Indianapolis, IN', 'Indianapolis, IN'), ('Jacksonville, FL', 'Jacksonville, FL'), ('Kansas City, MO', 'Kansas City, MO'), ('Las Vegas, NV', 'Las Vegas, NV'), ('Long Beach, CA', 'Long Beach, CA'), ('Los Angeles, CA', 'Los Angeles, CA'), ('Louisville, KY', 'Louisville, KY'), ('Memphis, TN', 'Memphis, TN'), ('Mesa, AZ', 'Mesa, AZ'), ('Miami, FL', 'Miami, FL'), ('Milwaukee, WI', 'Milwaukee, WI'), ('Minneapolis, MN', 'Minneapolis, MN'), ('Myrtle Beach, SC', 'Myrtle Beach, SC'), ('Nashville, TN', 'Nashville, TN'), ('New Orleans, LA', 'New Orleans, LA'), ('New York, NY', 'New York, NY'), ('Oakland, CA', 'Oakland, CA'), ('Oklahoma City, OK', 'Oklahoma City, OK'), ('Omaha, NE', 'Omaha, NE'), ('Philadelphia, PA', 'Philadelphia, PA'), ('Phoenix, AZ', 'Phoenix, AZ'), ('Portland, OR', 'Portland, OR'), ('Raleigh, NC', 'Raleigh, NC'), ('Sacramento, CA', 'Sacramento, CA'), ('San Antonio, TX', 'San Antonio, TX'), ('San Diego, CA', 'San Diego, CA'), ('San Francisco, CA', 'San Francisco, CA'), ('San Jose, CA', 'San Jose, CA'), ('Seattle, WA', 'Seattle, WA'), ('Tucson, AZ', 'Tucson, AZ'), ('Tulsa, OK', 'Tulsa, OK'), ('Virginia Beach, VA', 'Virginia Beach, VA'), ('Washington, DC', 'Washington, DC'), ('Wichita, KS', 'Wichita, KS'), ('Wilmington, NC', 'Wilmington, NC'), ('Winston-Salem, NC', 'Winston-Salem, NC')])
    date = DateField("Departure Date:", validators=[InputRequired(message='Please enter desired departure date'), DateRange(min = datetime.date.today(), message="Date must be greater than or equal to "+ str(datetime.date.today()))], format='%Y-%m-%d',)
    earliest_departure = TimeField("Earliest Time of Departure:", validators=[InputRequired(message='Please enter the earliest time of departure')], format='%H:%M')
    latest_departure = TimeField("Latest Time of Departure:", validators=[InputRequired(message='Please enter the latest time of departure'), GreaterThanEarliestDeparture()], format='%H:%M')
    seats_available = IntegerField("Number of Seats Available:", validators = [InputRequired(message='You must enter the number of seats available'),  NumberRange(min=1, max=8, message='You must enter a number of seats available between 1 and 8.')])
    gas_price = DecimalField("Gas Price (optional):", places=2, rounding=None, validators=[Optional(), NumberRange(min=0, message='Gas price must be a positive number or 0 if you don\'t want to charge the riders.')])
    comments = StringField("Comments (optional):", validators=[Optional()])
    submit = SubmitField("Submit")

class EditInfoFactory(FlaskForm):
    phone_number = StringField("Phone Number:", validators = [InputRequired(message='You must enter a valid phone number'), Regexp('^[0-9]', message = 'Please enter only numbers for phone number'), Length(min=10, max=12, message='Your phone number must be between 10 and 12 characters')])
    affiliation = SelectField("Affiliation:", choices = [('No Change', 'No Change'), ('Graduate', 'Graduate'), ('Undergraduate', 'Undergraduate')])
    license_plate_no = StringField("License Plate Number", validators = [OptionalIfNotDriver()])
    plate_state = SelectField("State", choices = [('No Change', 'No Change'), ('AL', 'AL'), ('AK', 'AK'), ('AZ', 'AZ'), ('AR', 'AR'), ('CA', 'CA'), ('CO', 'CO'), ('CT', 'CT'), ('DE', 'DE'), ('FL', 'FL'), ('GA', 'GA'), ('HI', 'HI'), ('ID', 'ID'), ('IL', 'IL'), ('IN', 'IN'), ('IA', 'IA'), ('KS', 'KS'), ('KY', 'KY'), ('LA', 'LA'), ('ME', 'ME'), ('MD', 'MD'), ('MA', 'MA'), ('MI', 'MI'), ('MN', 'MN'), ('MS', 'MS'), ('MO', 'MO'), ('MT', 'MT'), ('NE', 'NE'), ('NV', 'NV'), ('NH', 'NH'), ('NJ', 'NJ'), ('NM', 'NM'), ('NY', 'NY'), ('NC', 'NC'), ('ND', 'ND'), ('OH', 'OH'), ('OK', 'OK'), ('OR', 'OR'), ('PA', 'PA'), ('RI', 'RI'), ('SC', 'SC'), ('SD', 'SD'), ('TN', 'TN'), ('TX', 'TX'), ('UT', 'UT'), ('VT', 'VT'), ('VA', 'VA'), ('WA', 'WA'), ('WV', 'WV'), ('WI', 'WI'), ('WY', 'WY'), ('GU', 'GU'), ('PR', 'PR'), ('VI', 'VI')], default = 'No Change')
    currentPassword = PasswordField("Current password needed to make changes:", validators = [InputRequired(message='You must enter your password to confirm changes'), CorrectPassword()])
    password = PasswordField("New password:", validators = [Optional(), Length(min=5, max=100, message='Your password must be between 5 and 100 characters')])
    confirmPassword = PasswordField("Confirm Password:", validators = [Optional(), ConfirmPassEqual()]) 
    deleteAccount = SelectField("Would you like to delete your account? This action cannot be undone.", choices = [('No', 'No'), ('Yes','Yes')])
    submit = SubmitField("Save Changes")

class RideNumberFactory(FlaskForm):
    ride_no = IntegerField("Ride number:", validators = [InputRequired(message='You must enter a ride number')])
    submit = SubmitField("Enter")   

class EditRideFactory(FlaskForm):
    date = DateField("Departure Date:")
    earliest_departure = TimeField("Earliest Time of Departure:")
    latest_departure = TimeField("Latest Time of Departure:")
    gas_price = DecimalField("Gas Price:", places=2, rounding=None, validators=[NumberRange(min=0, message='Gas price must be a positive number or 0 if you don\'t want to charge the riders.')])
    comments = StringField("Comments:", validators=[Optional()])
    cancel = SelectField("Would you like to cancel this ride?", choices = [('No', 'No'), ('Yes', 'Yes')])
    submit = SubmitField("Save")

class EditReservationFactory(FlaskForm):
    spots_needed = IntegerField("Spots Needed:", validators = [InputRequired(message='You must enter spots needed')]) 
    cancel = SelectField("Would you like to cancel your reservation for this ride?", choices = [('No', 'No'), ('Yes', 'Yes')])
    submit = SubmitField("Save")

class ReserveRideFormFactory(FlaskForm):
    notes = StringField("Notes:", validators=[Optional()])
    submit = SubmitField("Request Ride")

class LogInFactory(FlaskForm):
    netid = StringField("NetID:", validators= [InputRequired(message='You must enter your NetID')])
    password = PasswordField("Password:", validators= [InputRequired(message='You must enter your password')])
    submit = SubmitField("Log in")

