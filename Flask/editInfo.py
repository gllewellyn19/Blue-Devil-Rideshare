from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template
import datetime 
from datetime import date

import models
import forms

def editInfo(editForm):
    user = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).first()
    driver = db.session.query(models.Driver).filter(models.Driver.netid == session['netid']).first()
    returnStatement = render_template('edit-info.html', user=user, editForm=editForm, driver=driver)

    if editForm.validate_on_submit():
        print("Edit form validated")
        newphone_number=request.form['phone_number']
        newaffiliation = request.form['affiliation']
        currentpassword = request.form['currentPassword']
        newpassword=request.form['password']
        confirmpassword = request.form['confirmPassword']
        plateNum = None
        plateState = None
        #Driver didn't necessarily change driver information, but default values in webpage
        if driver !=None:
            plateNum = request.form['license_plate_no']
            plateState = request.form['plate_state']
        
        #should be validator when phone number is a string
        if len(str(newphone_number))<6 or len(str(newphone_number))>10:
            flash("Your phone number must be at least 6 characters and no more than 10.")
            returnStatement = redirect(url_for('rides.editInfo_main'))
            return returnStatement

        #make validator- might not work
        if plateNum!=None and (len(plateNum)<2 or len(plateNum)>10):
            flash("Your plate number must be at least 2 characters and no more than 10.")
            returnStatement = redirect(url_for('rides.editInfo_main'))
            return returnStatement
        
        if currentpassword != user.password:
            flash("Password doesn't match current password. Changes could not be made.")
            returnStatement = redirect(url_for('rides.editInfo_main'))
            return returnStatement

        user_edit = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).one()
        #if the plate number is null and the user is a driver that means they deleted it from the default value
        if plateNum == None and driver !=None:
            flash("Must enter plate number.")
            returnStatement = redirect(url_for('rides.editInfo_main'))
            return returnStatement
        
        if newaffiliation != 'No Change':
            user_edit.affiliation = newaffiliation
        
        #if new password field wasn't empty then new password is equal to confirm password(validator)- only update password in this case
        if newpassword != '':
            #MAKE VALIDATOR- like function above check if it's null or if it's within some range
            if len(newpassword)<5 or len(newpassword)>100:
                flash("Your new password must be at least 5 characters and no more than 100")
                returnStatement = redirect(url_for('rides.editInfo_main'))
                return returnStatement

            if newpassword != user.password:
                flash("Password updated.") 
            user_edit.password = newpassword

        #can just do this even if they do not make any changes because default value in phone number field
        user_edit.phone_number = newphone_number
        db.session.commit()
        
        driver_edit = db.session.query(models.Driver).filter(models.Driver.netid == session['netid']).first()
        #return now if do not need to update driver information
        if driver_edit == None:
            flash("User information updated.")
            returnStatement = redirect(url_for('rides.account_main')) 
            return returnStatement

        driver_edit.license_plate_no = plateNum
        if plateState != 'No Change':
            driver_edit.plate_state = plateState
        db.session.commit()
        
        flash("User information updated.")
        returnStatement = redirect(url_for('rides.account_main'))
        return returnStatement
    else:
        print("didnt validate")

    
    return returnStatement