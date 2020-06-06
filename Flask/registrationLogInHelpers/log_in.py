from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template

import forms
import models

def sign_in():
    logInForm = forms.LogInFactory()

    if logInForm.validate_on_submit():
        netid = request.form['netid']
        password = request.form['password']
        user = models.Rideshare_user.query.filter_by(netid=netid).first()

        if not user or not (user.password==password):
            flash('Invalid Credentials. Please try again.')
            return redirect(url_for('rides.log_in_main'))
        else:
            set_session(netid)
            return redirect(url_for('rides.home_page'))
            
    return render_template('registerLogInPages/log-in.html', form=logInForm)

def set_session(netid):
    session['logged_in'] = True
    session['netid'] = netid
    driver = models.Driver.query.filter_by(netid=netid).first()
    if not driver:
        session['driver'] = False
    else:
        session['driver'] = True