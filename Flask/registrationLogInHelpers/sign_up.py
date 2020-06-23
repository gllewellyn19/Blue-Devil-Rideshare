from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for, render_template

import models
import forms

#controls the creation of the account
def create_account():
    signUpForm = forms.RegisterFormFactory()

    if signUpForm.validate_on_submit():
        netid,name,duke_email,phone_number,password,affiliation=extract_info(signUpForm)
        if check_existing_user(netid):
            return redirect(url_for('rides.log_in_main'))

        register_user(netid,name,duke_email,phone_number,password,affiliation)
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
    return netid,name,duke_email,phone_number,password,affiliation

#returns true if the given netid already goes with an existing account
def check_existing_user(netid):
    existingUsers = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == netid)
    if existingUsers.first() != None:
        flash("An account with this netid already exists. Please log in.")
        return True
    return False

#inserts the user into the database
def register_user(netid,name,duke_email,phone_number,password,affiliation):
    #NOTE try to do this with prepare statement but not working
    """db.session.execute('''PREPARE signUp (varchar, varchar, varchar, integer, varchar, varchar)\
        AS INSERT INTO Rideshare_user VALUES ($1, $2, $3, $4, $5, $6);''')
    newUser = db.session.execute('EXECUTE signUp(:netid, :name, :duke_email, :phone_number, :password, :affiliation)',\
            {"netid":session['netid'], "name":name, "duke_email":duke_email, "phone_number":phone_number, "password":password,\
            "affiliation":affiliation})
    db.session.commit()
    db.session.execute('DEALLOCATE signUp')"""
    newUser = models.Rideshare_user(netid=netid, name=name, duke_email=duke_email, phone_number=phone_number, password=password,\
        affiliation=affiliation)
    db.session.add(newUser)
    db.session.commit()
    flash("Account successfully created.")
