from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for, render_template

import models
import forms

def create_account():
    """
    Handles the user signing up to create an account
    Redirects them to the log in page with a message after if successful
    """
    signUpForm = forms.RegisterFormFactory()

    if signUpForm.validate_on_submit():
        netid,name,duke_email,phone_number,affiliation,password=extract_info(signUpForm)
        #everything checked with vaildators so just can register user
        register_user(netid,name,duke_email,phone_number,affiliation,password)
        return redirect(url_for('rides.log_in_main'))
        
    return render_template('registerLogInPages/sign-up.html', form=signUpForm)

def extract_info(form):
    """
    Extracts the data from the form and puts it into variables to return
    """
    netid = request.form['netid']
    name = request.form['name']
    duke_email = request.form['duke_email']
    phone_number = request.form['phone_number']
    password = request.form['password']
    affiliation = request.form['affiliation_sel']
    return netid,name,duke_email,phone_number,affiliation,password

def register_user(netid,name,duke_email,phone_number,affiliation,password):
    """
    Inserts the user into the database
    """
    db.session.execute('''PREPARE SignUp (varchar, varchar, varchar, varchar, varchar, varchar)\
        AS INSERT INTO Rideshare_user VALUES ($1, $2, $3, $4, $5, $6);''')
    newUser = db.session.execute('EXECUTE SignUp(:netid, :name, :duke_email, :phone_number, :affiliation, :password)',\
            {"netid":netid, "name":name, "duke_email":duke_email, "phone_number":phone_number, "affiliation":affiliation,\
            "password":password})
    db.session.commit()
    db.session.execute('DEALLOCATE SignUp')
    flash("Account successfully created.")
