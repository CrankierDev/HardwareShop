import copy
import csv
import os

import pandas as pd
from flask import request

from models import *


# Find an user or product in function of a given key.
# This function is used all over the application.
def finder(key, value):
    if key == 'customer':
        result = db.session.query(Customer).filter_by(nif=value).first()

    elif key == 'supplier':
        result = db.session.query(Supplier).filter_by(nif=value).first()

    elif key == 'product':
        result = db.session.query(Product).filter_by(name=value).first()

    return result


'''
    This file manages all the shopping cart actions.
'''


# Add a new shopping cart to the customer attributes
def createCart(customer):
    cartPath = 'database/shoppingCarts/'
    fileName = customer.nif + '.csv'
    customer.shoppingCart = cartPath + fileName

    carts = os.listdir(cartPath)
    # print(carts)

    if fileName not in carts:
        print('Creating shopping cart...')

        newCSV = open(customer.shoppingCart, "w")
        writer = csv.writer(newCSV)
        writer.writerow(['ProductName', 'Quantity'])

        del writer
        newCSV.close()


# Adds products to customers carts
def addNewProduct(customer, name, quantity=1):
    createCart(customer)
    productInList = False

    file = open(customer.shoppingCart, "r")
    reader = csv.DictReader(file)

    for row in reader:
        if row['ProductName'] == name:
            productInList = True
            break

    del reader
    file.close()

    if not productInList:
        file = open(customer.shoppingCart, "a")
        writer = csv.writer(file)
        writer.writerow([name, quantity])

        del writer
        file.close()


# Exports CSV info to a variable
def decodeCSV(customer):
    # addNewProduct(customer, 'INTEL CORE I9 - 10900K', 1)
    createCart(customer)

    file = open(customer.shoppingCart, "r")
    reader = csv.DictReader(file)

    productsList = []

    for row in reader:
        productObject = finder('product', row['ProductName'])
        row['ProductName'] = productObject
        productsList.append(row)

    del reader
    file.close()

    # print(productsList)
    return productsList


# Delete products to customers carts
def deleteProduct(customer, name):
    file = customer.shoppingCart

    df = pd.read_csv(file)
    df = df[df.ProductName != name]

    df.to_csv(file, index=False)


# Gives back the quantity of each product
def catchQuantity(customer):
    totalAmount = 0
    products = decodeCSV(customer)

    for product in products:
        name = "buyQuantity-" + product['ProductName'].name
        quantity = int(request.form[name])
        product['Quantity'] = quantity
        totalAmount += product['ProductName'].price * product['Quantity']

    refreshCSVQuantities(customer, products)

    return products, totalAmount


# Save actual info to shopping cart csv
def refreshCSVQuantities(customer, products):
    os.remove(customer.shoppingCart)

    data = copy.deepcopy(products)

    for datarow in data:
        datarow['ProductName'] = datarow['ProductName'].name

    # Create a new data frame and export it to a CSV
    df = pd.DataFrame.from_dict(data)
    df.to_csv(customer.shoppingCart, index=False, header=True)


# Deletes the entire csv file in order to restart the chart for the next purchase and take
# in count the expenses on stock
def deleteCart(customer, maxQuantity):
    products = decodeCSV(customer)

    for product in products:
        stockController('customer', product, maxQuantity)

    os.remove(customer.shoppingCart)


# Manages stocks for refills and sells
def stockController(key, product, maxQuantity):
    if key == 'customer':
        product['ProductName'].quantity -= int(product['Quantity'])
        product['ProductName'].stock = (product['ProductName'].quantity / maxQuantity) * 100
        product['ProductName'].soldQuantity += int(product['Quantity'])

        if product['ProductName'].quantity < 0:
            product['ProductName'].quantity = 0
            product['ProductName'].stock = 0

    elif key == 'supplier':
        product['ProductName'].quantity = maxQuantity
        product['ProductName'].stock = 100
