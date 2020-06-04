from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template
import datetime 
from datetime import date

import models
import forms

def editInfo(editForm):
    
    user = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).first()
    driver = db.session.query(models.Driver).filter(models.Driver.netid == session['netid']).first()

    if editForm.validate_on_submit():
        user_edit = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).one()
        driver_edit = db.session.query(models.Driver).filter(models.Driver.netid == session['netid']).first()

        newphone_number=request.form['phone_number']
        newaffiliation = request.form['affiliation']
        currentpassword = request.form['currentPassword']
        newpassword=request.form['password']
        confirmpassword = request.form['confirmPassword']
        plateNum = None
        plateState = None

        #delete the user's account if requested (don't make any other changes)
        if request.form['deleteAccount']=='Yes':
            if driver_edit!=None:
                db.session.delete(driver_edit)
                db.session.commit()
                session['driver']=False #works if not driver?

            db.session.delete(user_edit)
            db.session.commit()
            session['netid']=False
            session['logged_in']= False
            flash("Your account has been deleted.")
            return redirect(url_for('rides.home_page'))

        #Driver didn't necessarily change driver information, but default values in webpage
        if driver != None:
            plateNum = request.form['license_plate_no']
            plateState = request.form['plate_state']
        
        #should be validator when phone number is a string
        if len(str(newphone_number))<6 or len(str(newphone_number))>10:
            flash("Your phone number must be at least 6 characters and no more than 10.")
            return redirect(url_for('rides.editInfo_main'))
        
        if newaffiliation != 'No Change':
            user_edit.affiliation = newaffiliation
        
        #if new password field wasn't empty then new password is equal to confirm password(validator)- only update password in this case
        if newpassword != '':
            user_edit.password = newpassword

        #can just do this even if they do not make any changes because default value in phone number field
        user_edit.phone_number = newphone_number
        db.session.commit()
        
        #return now if do not need to update driver information
        if driver_edit == None:
            flash("User information updated.")
            return redirect(url_for('rides.account_main')) 

        driver_edit.license_plate_no = plateNum
        if plateState != 'No Change':
            driver_edit.plate_state = plateState
        db.session.commit()
        
        flash("User information updated.")
        return redirect(url_for('rides.account_main'))

    
    return render_template('edit-info.html', user=user, editForm=editForm, driver=driver)