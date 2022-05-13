from sqlalchemy import Column, Integer, String, Boolean, Float

import db


class Product(db.Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(1000), nullable=False)
    category = Column(String(100), nullable=False)
    storageLocation = Column(String(300), nullable=False)
    imgRoute = Column(String(300), nullable=False)
    quantity = Column(Integer, nullable=False)
    maximumQuantity = Column(Integer, nullable=False)
    stock = Column(Float, nullable=False)
    brand = Column(String(100), nullable=False)
    offer = Column(Boolean, nullable=False)
    offerQuantity = Column(Integer, nullable=True)
    priceOrig = Column(Float, nullable=True)

    def __init__(self, name, category, price, description, storageLocation,
                 imgRoute, quantity, maximumQuantity, brand, offer=False, offerQuantity=0, priceOrig=None):
        self.name = name
        self.category = category
        self.price = price
        self.description = description
        self.storageLocation = storageLocation
        self.imgRoute = imgRoute
        self.quantity = quantity
        self.maximumQuantity = maximumQuantity
        self.stock = (quantity/maximumQuantity)*100
        self.brand = brand
        self.offer = offer
        self.offerQuantity = offerQuantity

        if priceOrig is None:
            self.priceOrig = self.price
        else:
            self.priceOrig = priceOrig

    def __repr__(self):
        return """
        Producto {}:
        - Brand: {}.
        - Categoria: {}.
        - Precio: {}.
        - Descripcion: {}.
        - Localizacion en almacen: {}.
        - Stock en almacen: {}.""".format(self.name, self.brand, self.category, self.price,
                                          self.description, self.storageLocation, self.stock)

    def __str__(self):
        return """
        Producto {}:
        - Brand: {}.
        - Categoria: {}.
        - Precio: {}.
        - Descripcion: {}.
        - Localizacion en almacen: {}.
        - Stock en almacen: {}.""".format(self.name, self.brand, self.category, self.price,
                                          self.description, self.storageLocation, self.stock)



class Customer(db.Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(100), nullable=False)
    nif = Column(String(9), nullable=False)
    address = Column(String(200), nullable=False)
    cp = Column(Integer, nullable=False)
    city = Column(String(100), nullable=False)
    phone = Column(String(100), nullable=False)
    mail = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    shoppingCart = Column(String(300), nullable=True)

    def __init__(self, name, surname, nif, address, cp, city, phone, mail, password):
        self.name = name
        self.surname = surname
        self.nif = nif
        self.address = address
        self.cp = cp
        self.city = city
        self.phone = phone
        self.mail = mail
        self.password = password

    def __repr__(self):
        return """
        Cliente {} {}:
        - NIF: {}.
        - Direccion: {}, {}, {}.
        - Contacto:
            e-mail : {}.
            telefono: {}.""".format(self.name, self.surname, self.nif, self.address, self.cp, self.city,
                                    self.mail, self.phone)

    def __str__(self):
        return """
        Cliente {} {}:
        - NIF: {}.
        - Direccion: {}, {}, {}.
        - Contacto:
            e-mail : {}.
            telefono: {}.""".format(self.name, self.surname, self.nif, self.address, self.cp, self.city,
                                    self.mail, self.phone)


class Supplier(db.Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    nif = Column(String(9), nullable=False)
    address = Column(String(200), nullable=False)
    cp = Column(Integer, nullable=False)
    city = Column(String(100), nullable=False)
    phone = Column(Integer, nullable=False)
    mail = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)

    def __init__(self, name, nif, address, cp, city, phone, mail, password):
        self.name = name
        self.nif = nif
        self.address = address
        self.cp = cp
        self.city = city
        self.phone = phone
        self.mail = mail
        self.password = password

    def __repr__(self):
        return """
        Cliente {}:
        - NIF: {}.
        - Direccion: {}, {}, {}.
        - Contacto:
            e-mail : {}.
            telefono: {}.""".format(self.name, self.nif, self.address, self.cp, self.city,
                                    self.mail, self.phone)

    def __str__(self):
        return """
        Cliente {}:
        - NIF: {}.
        - Direccion: {}, {}, {}.
        - Contacto:
            e-mail : {}.
            telefono: {}.""".format(self.name, self.nif, self.address, self.cp, self.city,
                                    self.mail, self.phone)