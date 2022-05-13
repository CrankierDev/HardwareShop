from flask import Flask, render_template, url_for, request, redirect
from models import *


'''
    This file manages all the sign actions. 
'''


# Ensure admin existence in system
def adminWatcher(key):

    if key == 'customer':
        queryList = db.session.query(Customer.name).all()

    elif key == 'supplier':
        queryList = db.session.query(Supplier.name).all()

    cleanQueryList = cleanData(queryList)

    if 'admin' in cleanQueryList:
        pass
    else:
        adminCreator()


# Remove characters that we do not want in queries
def cleanData(data):
    dataClean = []

    for i in range(len(data)):
        dataClean.append(data[i][0])

    return dataClean


# Create an predetermined admin user
def adminCreator():
    name = 'admin'
    surname = 'admin'
    nif = "12345678A"
    address = 'adminAddress'
    cp = '12345'
    city = 'adminCity'
    phone = 987654321
    mail = 'admin'
    password = 'admin'

    adminCustomer = Customer(name, surname, nif, address, cp, city, phone, mail, password)
    adminSupplier = Supplier(name, nif, address, cp, city, phone, mail, password)

    db.session.add(adminCustomer)
    db.session.add(adminSupplier)

    db.session.commit()


# Take the data posted in form and works with it
def catchData(keySign, keyPerson):

    if keySign == 'sign-in':
        userMail = request.form['userMail']
        userPassword = request.form['userPassword']

        return userMail, userPassword

    elif keySign == 'sign-up':
        name = request.form['name']
        nif = request.form['nif']
        address = request.form['address']
        cp = request.form['cp']
        city = request.form['city']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        emailRepeat = request.form['emailRepeat']
        passwordRepeat = request.form['passwordRepeat']

        verification = emailPassVerify(email, password, emailRepeat, passwordRepeat)

        if keyPerson == 'customer':
            surname = request.form['surname']
            return name, surname, nif, address, cp, city, phone, email, password, verification

        elif keyPerson == "supplier":
            return name, nif, address, cp, city, phone, email, password, verification


# Verifier for double-check entries for email and password
def emailPassVerify(email, password, emailRepeat, passwordRepeat):
    if email == emailRepeat and password == passwordRepeat:
        print('Usuario válido')
        return True

    else:
        print('Usuario NO válido')
        return False


# Verify if an user is signed up in the database and check if mail and pswd are OK
def verifyKeys(mail, password, key):
    if key == "customer":
        emailList = db.session.query(Customer.mail).all()
    elif key == "supplier":
        emailList = db.session.query(Supplier.mail).all()

    cleanEmailList = cleanData(emailList)

    # print(cleanEmailList)

    if mail in cleanEmailList:
        if key == "customer":
            pwd = db.session.query(Customer.password).filter_by(mail=mail).first()
        elif key == "supplier":
            pwd = db.session.query(Supplier.password).filter_by(mail=mail).first()

        # print(pwd[0], password)

        if password == pwd[0]:
            return True

        else:
            return False

    return False















