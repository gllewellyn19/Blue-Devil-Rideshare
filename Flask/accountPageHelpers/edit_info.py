from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template
import datetime 
from datetime import date

import models
import forms

def update():
    """
    Updates the user's info from the accounts page
    """
    editForm = forms.EditInfoFactory()
    user = db.session.query(models.Rideshare_user).filter(models.Rideshare_user.netid == session['netid']).first()
    driver = db.session.query(models.Driver).filter(models.Driver.netid == session['netid']).first()

    if editForm.validate_on_submit():
        newphone_number,newaffiliation,currentpassword,newpassword,confirmpassword,plateNum,plateState = extract_info(driver, editForm)

        #delete the user's account if requested (don't make any other changes to account)
        if request.form['deleteAccount']=='Yes':
            delete_account(driver, user)
            return redirect(url_for('rides.home_page'))

        make_account_changes(user, newaffiliation, newpassword, newphone_number)
        
        #update the driver information if the user is a driver
        if driver != None:
            update_driver_info(driver, plateNum, plateState)
        
        flash("User information updated.")
        return redirect(url_for('rides.account_main'))

    return render_template('accountPages/edit-info.html', user=user, driver=driver, editForm=editForm)

def extract_info(driver, form):
    """
    Extracts the data from the form and stores it in variables 
    """
    newphone_number=request.form['phone_number']
    newaffiliation = request.form['affiliation']
    currentpassword = request.form['currentPassword']
    newpassword=request.form['password']
    confirmpassword = request.form['confirmPassword']
    plateNum = None
    plateState = None
    #Driver didn't necessarily change driver information, but default values in webpage
    if driver != None:
        plateNum = request.form['license_plate_no']
        plateState = request.form['plate_state']
    return newphone_number,newaffiliation,currentpassword,newpassword,confirmpassword,plateNum,plateState

def delete_account(driver, user):
    """
    Deletes the users account and driver entry if they are a driver
    """
    #delete driver entry in table if necessary
    if driver!=None:
        db.session.delete(driver)
        db.session.commit()
        session['driver']=False 

    db.session.delete(user)
    db.session.commit()
    session['netid']=False
    session['logged_in']= False
    flash("Your account has been deleted.")

def make_account_changes(user, newaffiliation, newpassword, newphone_number):
    """
    Changes the affiliation, password and phone number of the users account 
    """
    if newaffiliation != 'No Change':
        user.affiliation = newaffiliation
        
    #if new password field wasn't empty then new password is equal to confirm password(validator)- only update password in this case
    if newpassword != '':
        user.password = newpassword

    #can just do this even if they do not make any changes because default value in phone number field
    user.phone_number = newphone_number
    db.session.commit()

def update_driver_info(driver, plateNum, plateState):
    """
    Updates the driver information if the user is a driver (default values mean you can just update without checking for change)
    """
    driver.license_plate_no = plateNum
    if plateState != 'No Change':
        driver.plate_state = plateState
    db.session.commit()