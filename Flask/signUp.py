from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for, render_template

import models
import forms

def sign_up(signupForm):

    if signupForm.validate_on_submit():
        netid = request.form['netid']
        name = request.form['name']
        duke_email = request.form['duke_email']
        phone_number = request.form['phone_number']
        password = request.form['password']
        affiliation = request.form['affiliation_sel']
        school = request.form['school']
        #change to phone number to varchar when I change later
        

        #easy fix when I make phone number a string
        if len(str(phone_number))<6 or len(str(phone_number))>10:
            flash("Your phone number must be at least 6 characters and no more than 10.")
            return redirect(url_for('rides.sign_up_main'))

        existingUsers = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == netid)
        if existingUsers.first() != None:
            flash("An account with this netid already exists. Please log in.")
            return redirect(url_for('rides.log_in_main'))

        #NOTE try to do this with prepare statement but not working
        """db.session.execute('''PREPARE signUp (varchar, varchar, varchar, integer, varchar, varchar, varchar)\
            AS INSERT INTO Rideshare_user VALUES ($1, $2, $3, $4, $5, $6, $7);''')
        newUser = db.session.execute('EXECUTE signUp(:netid, :name, :duke_email, :phone_number, :password, :affiliation, :school)', {"netid":netid, "name":name, "duke_email":duke_email, "phone_number":phone_number, "password":password, "affiliation":affiliation, "school":school})
        db.session.commit()
        db.session.execute('DEALLOCATE signUp')"""
        register = models.Rideshare_user(netid=netid, name=name, duke_email=duke_email, phone_number=phone_number, password=password, affiliation=affiliation, school=school)
        db.session.add(register)
        db.session.commit()

        flash("Account successfully created.")
        return redirect(url_for('rides.log_in_main'))
    return render_template('sign-up.html', form=signupForm)