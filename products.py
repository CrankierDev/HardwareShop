import os
import db

from models import Product
from logs import cleanData

from flask import request

'''
    This file manages all the home  pages and product actions.
'''


# Read txt's which include product information
def infoProducts(path):
    fileName = 'README.txt'
    pathTXT = path + '/' + fileName

    file = open(pathTXT, 'r', encoding="utf-8")
    info = {}

    file.seek(0)
    for i, line in enumerate(file):
        # print(line)

        if i == 1:
            correctedLine = infoPostprocess(line)
            info["name"] = correctedLine

        if i == 3:
            correctedLine = infoPostprocess(line)
            info["pvp"] = correctedLine

        if i == 5:
            correctedLine = infoPostprocess(line)
            info["description"] = correctedLine

        if i == 7:
            correctedLine = infoPostprocess(line)
            info["category"] = correctedLine

        if i == 9:
            correctedLine = infoPostprocess(line)
            info["storageLocation"] = correctedLine

        if i == 11:
            correctedLine = infoPostprocess(line)
            info["brand"] = correctedLine

    file.close()

    return info


# Info postprocessor
def infoPostprocess(line):
    if line.endswith("\n"):
        chains = line.split('\n')
        newLine = chains[0]
    else:
        newLine = line

    return newLine


# Read txt's which include product information
def infoOffers(path):
    fileName = 'OFFER.txt'
    pathTXT = path + '/' + fileName

    file = open(pathTXT, 'r', encoding="utf-8")
    offer = {}

    file.seek(0)
    for i, line in enumerate(file):
        # print(line)

        if i == 1:
            correctedLine = infoPostprocess(line)
            offer["offer"] = correctedLine

        if i == 3:
            correctedLine = infoPostprocess(line)
            offer["offerQuantity"] = correctedLine

    file.close()

    return offer


# Parse all data that need to be float or any other type
def parserInfo(info):
    keys = info.keys()

    if 'name' in keys:
        info['name'] = info['name'].upper()

    if 'pvp' in keys and info['pvp'] != '':
        info['pvp'] = float(info['pvp'])

    if 'priceOrig' in keys  and info['priceOrig'] != '':
        info['priceOrig'] = float(info['priceOrig'])

    if 'brand' in keys:
        info['brand'] = info['brand'].capitalize()

    if 'category' in keys:
        info['category'] = info['category'].lower()

    if 'offerQuantity' in keys and info['offerQuantity'] != '':
        info['offerQuantity'] = float(info['offerQuantity'])

    elif 'offerQuantity' in keys and info['offerQuantity'] == '':
        info['offerQuantity'] = 0

    if 'offer' in keys:
        if info['offer'] == 'True':
            info['offer'] = True

        else:
            info['offer'] = False


# Let's add IVA to prices.
def addIVA(pvp, IVA = 21):
    percentageIVA = IVA / 100

    return pvp * (1 + percentageIVA)


# Returns data from 'OFFER.txt' after working with it
def offerData(path, pvp):
    offerInfo = infoOffers(path)
    parserInfo(offerInfo)
    # print(offerInfo['offer'])

    if offerInfo['offer'] is False:
        actualPrice = pvp

    else:
        actualPrice = pricing(pvp, offerInfo["offerQuantity"])

    return actualPrice, offerInfo


# Let's define a pricing function which interacts with offers.
def pricing(pvp, offerQuantity):
    percentageOffer = offerQuantity / 100

    offerPrice = pvp * (1 - percentageOffer)

    return offerPrice


# Refresh the skills data
def refreshProducts(IVA, maxQuantity):
    root = "static/products/stock/"  # root path for products
    folders = os.listdir(root)  # products categories

    productsList = db.session.query(Product.name).all()
    productsList = cleanData(productsList)

    # print(folders, "\n",productsList)

    for folder in folders:
        if folder == 'desktop.ini':  # Subroutine for skipping automatic file created by my pc
            continue

        pathFold = root + folder
        elements = os.listdir(pathFold)  # Gives a file/folder list for the directory

        # print(pathFold, "\n", elements)

        for element in elements:
            if element == 'desktop.ini':  # Subroutine for skipping automatic file created by my pc
                continue

            path = pathFold + '/' + element  # Another option: os.path.join(pathFold, element)
            innerElements = os.listdir(path)  # Elements listed in path

            if element not in productsList:
                pathImg = '../../' + path + '/img.png'
                # print(pathImg)

                fileInfo = infoProducts(path)
                parserInfo(fileInfo)

                fileInfo['pvp'] = addIVA(fileInfo['pvp'], IVA)

                if 'OFFER.txt' in innerElements:
                    actualPrice, offerInfo = offerData(path, fileInfo['pvp'])

                    newProduct = Product(fileInfo['name'], fileInfo['category'], actualPrice, fileInfo['description'],
                                         fileInfo['storageLocation'], pathImg, maxQuantity, maxQuantity, fileInfo['brand'],
                                         offerInfo['offer'], offerInfo['offerQuantity'], fileInfo['pvp'])

                else:
                    newProduct = Product(fileInfo['name'], fileInfo['category'], fileInfo['pvp'], fileInfo['description'],
                                         fileInfo['storageLocation'], pathImg, maxQuantity, maxQuantity, fileInfo['brand'])

                db.session.add(newProduct)


            elif element in productsList:
                product = db.session.query(Product).filter_by(name=element).first()
                # print(product)

                if 'OFFER.txt' in innerElements:
                    actualPrice, offerInfo = offerData(path, product.priceOrig)

                    product.price = actualPrice
                    product.offer = offerInfo['offer']
                    product.offerQuantity = offerInfo['offerQuantity']


                else:
                    product.price = product.priceOrig
                    product.offer = False
                    product.offerQuantity = 0


    db.session.commit()


# Catch data from new products and works with it
def catchProduct(supplier, key, selectedProduct=None):
    data = {
        'name': request.form['name'],
        'priceOrig': request.form['pvp'],
        'description': request.form['description'],
        'category': request.form['category'],
        'offer': request.form['offer'],
        'offerQuantity': request.form['offerQuantity']}

    parserInfo(data)

    if key == 'new':
        data['img'] = request.files['img']
        data['brand'] = supplier.name
        data['storageLocation'] = 'A determinar en almacen'

    if key == 'new':
        createFiles(data)

    else:
        path = "static/products/stock/" + selectedProduct.category + '/' + selectedProduct.name + '/'
        editFiles(data, path, selectedProduct)

    # print(data)


# Create files for categories, and new products
def createFiles(data):
    path = "static/products/stock/"
    pathFold = path + data['category'] + '/'

    innerElements = os.listdir(path)

    if data['category'] not in innerElements:
        os.mkdir(pathFold)

    # Error handling to have under control files previously created.
    try:
        if data['name'] in os.listdir(pathFold):
            raise Exception()

    except Exception:
        print('This product already exist!')

    else:
        pathFiles = pathFold + data['name'] + '/'
        os.mkdir(pathFiles)

        # Build README.txt file to have a registry of the products info
        readmeFile = open(pathFiles + 'README.txt', 'w')

        readmeFile.write('name:\n')
        readmeFile.write(data['name'])
        readmeFile.write('\n')
        readmeFile.write('PVP:\n')
        readmeFile.write(str(data['priceOrig']))
        readmeFile.write('\n')
        readmeFile.write('description:\n')
        readmeFile.write(data['description'])
        readmeFile.write('\n')
        readmeFile.write('category:\n')
        readmeFile.write(data['category'])
        readmeFile.write('\n')
        readmeFile.write('storageLocation:\n')
        readmeFile.write(data['storageLocation'])
        readmeFile.write('\n')
        readmeFile.write('brand:\n')
        readmeFile.write(data['brand'])

        readmeFile.close()


        # Build OFFER.txt file to have a registry of the products info
        offerFile = open(pathFiles + 'OFFER.txt', 'w')

        offerFile.write('offer:\n')
        offerFile.write(str(data['offer']))
        offerFile.write('\n')
        offerFile.write('offerQuantity:\n')
        offerFile.write(str(data['offerQuantity']))

        offerFile.close()


        # Upload the img file to the pathfolder of the product
        data['img'].filename = 'img.png'
        # print(data['img'].filename)
        data['img'].save(os.path.join(pathFiles, data['img'].filename))


# Edit files for existing products
def editFiles(data, path, product):
    innerElements = os.listdir(path)

    if 'README.txt' not in innerElements:
        with open(path+'README.txt', 'w') as readmeFile:
            readmeFile.write('name:\n')
            readmeFile.write(' \n')
            readmeFile.write('PVP:\n')
            readmeFile.write(' \n')
            readmeFile.write('description:\n')
            readmeFile.write(' \n')
            readmeFile.write('category:\n')
            readmeFile.write(' \n')
            readmeFile.write('storageLocation:\n')
            readmeFile.write(' \n')
            readmeFile.write('brand:\n')
            readmeFile.write(' \n')

    if 'OFFER.txt' not in innerElements:
        with open(path+'OFFER.txt', 'w') as offerFile:
            offerFile.write('offer:\n')
            offerFile.write('False \n')
            offerFile.write('offerQuantity:\n')
            offerFile.write(' \n')

    with open(path+'README.txt', 'r') as file:
        # Read a list of lines into readme
        readme = file.readlines()

    print('Old readme file:\n')
    print(readme)

    if data['name'] != '':
        readme[1] = data['name'] + '\n'
        product.name = data['name']
    if data['priceOrig'] != '':
        readme[3] = str(data['priceOrig']) + '\n'
        product.priceOrig = addIVA(data['priceOrig'])
    if data['description'] != '':
        readme[5] = data['description'] + '\n'
        product.description = data['description']
    if data['category'] != '':
        readme[7] = data['category'] + '\n'
        product.category = data['category']

    # and write everything back with changes
    with open(path+'README.txt', 'w') as file:
        file.writelines(readme)

    print('New readme file:\n')
    print(readme)


    with open(path+'OFFER.txt', 'r') as file:
        # read a list of lines into offer
        offer = file.readlines()

    print('Old offer file:\n')
    print(offer)

    if data['offer'] != '':
        offer[1] = str(data['offer']) + '\n'
        product.offer = data['offer']

    if data['offerQuantity'] != '':
        offer[3] = str(data['offerQuantity']) + '\n'
        product.offerQuantity = data['offerQuantity']

    # and write everything back with changes
    with open(path+'OFFER.txt', 'w') as file:
        file.writelines(offer)

    print('New offer file:\n')
    print(offer)

