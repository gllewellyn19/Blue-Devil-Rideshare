from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template

import forms
import models


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
            session['netid'] = netid
            driver = models.Driver.query.filter_by(netid=session['netid']).first()
            if not driver:
                session['driver'] = False
            else:
                session['driver'] = True
            return redirect(url_for('rides.home_page'))
            
    return render_template('log-in.html', error=error)