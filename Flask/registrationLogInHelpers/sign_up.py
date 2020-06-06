from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for, render_template

import models
import forms

def create_account():
    signUpForm = forms.RegisterFormFactory()

    if signUpForm.validate_on_submit():
        netid,name,duke_email,phone_number,password,affiliation,school=extract_info(signUpForm)
        if check_existing_user(netid):
            return redirect(url_for('rides.log_in_main'))

        register_user(netid,name,duke_email,phone_number,password,affiliation,school)
        return redirect(url_for('rides.log_in_main'))
        
    return render_template('registerLogInPages/sign-up.html', form=signUpForm)

#extracts the data from the form and puts it into variables
def extract_info(form):
    netid = request.form['netid']
    name = request.form['name']
    duke_email = request.form['duke_email']
    phone_number = request.form['phone_number']
    password = request.form['password']
    affiliation = request.form['affiliation_sel']
    school = request.form['school']
    #NOTE: change to phone number to varchar when I change later and remove school
    return netid,name,duke_email,phone_number,password,affiliation,school

#returns true if the given netid already goes with an existing account
def check_existing_user(netid):
    existingUsers = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == netid)
    if existingUsers.first() != None:
        flash("An account with this netid already exists. Please log in.")
        return True
    return False

#inserts the user into the data base
def register_user(netid,name,duke_email,phone_number,password,affiliation,school):
    #NOTE try to do this with prepare statement but not working
    """db.session.execute('''PREPARE signUp (varchar, varchar, varchar, integer, varchar, varchar, varchar)\
        AS INSERT INTO Rideshare_user VALUES ($1, $2, $3, $4, $5, $6, $7);''')
    newUser = db.session.execute('EXECUTE signUp(:netid, :name, :duke_email, :phone_number, :password, :affiliation, :school)',\
            {"netid":session['netid'], "name":name, "duke_email":duke_email, "phone_number":phone_number, "password":password, "affiliation":affiliation, "school":school})
    db.session.commit()
    db.session.execute('DEALLOCATE signUp')"""
    newUser = models.Rideshare_user(netid=netid, name=name, duke_email=duke_email, phone_number=phone_number, password=password, affiliation=affiliation, school=school)
    db.session.add(newUser)
    db.session.commit()
    flash("Account successfully created.")
