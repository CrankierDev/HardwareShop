from logs import *

from products import refreshProducts, catchProduct
from shoppingCarts import *

app = Flask(__name__)

# Global variables used all over the application.
IVA = 21  # IVA taxes
maxQuantity = 10  # Max quantity to store of the products

'''
    This section is the one where logins are managed. All sign-in's and sign-up's
    were done here
'''


# Simple entry page to select if you are going to customers or suppliers page.
@app.route('/')
def home():
    return render_template('index.html')


# Sign in screen
@app.route('/login/<user>/<attempt>')
def login(user, attempt):
    adminWatcher(user)

    return render_template("sign-in.html", user=user, attempt=attempt)


# Sign in redirection to home
@app.route('/signed-in/<user>/<attempt>', methods=['POST'])
def signedIn(user, attempt):
    mail, password = catchData('sign-in', user)
    verification = verifyKeys(mail, password, user)

    if verification:
        if user == "customer":
            person = db.session.query(Customer).filter_by(mail=mail).first()

        elif user == "supplier":
            person = db.session.query(Supplier).filter_by(mail=mail).first()

        # print(person.nif)

        return redirect(url_for('logged', key=user, nif=person.nif))

    else:
        attempt = 'retry'
        return redirect(url_for('login', user=user, attempt=attempt))


# Sign up screen
@app.route('/sign-up/<user>/<attempt>')
def signUp(user, attempt):
    return render_template("sign-up.html", user=user, attempt=attempt)


# Sign up redirection to home
@app.route('/signed-up/<user>/<attempt>', methods=['POST'])
def signedUp(user, attempt):
    if user == "customer":
        name, surname, nif, address, cp, city, phone, email, password, verification = catchData('sign-up', user)

    elif user == "supplier":
        name, nif, address, cp, city, phone, email, password, verification = catchData('sign-up', user)

    if verification and user == "customer":
        newperson = Customer(name, surname, nif, address, cp, city, phone, email, password)

        db.session.add(newperson)
        db.session.commit()

        return redirect(url_for('logged', key=user, nif=newperson.nif))

    elif verification and user == "supplier":
        newperson = Supplier(name, nif, address, cp, city, phone, email, password)

        db.session.add(newperson)
        db.session.commit()

        return redirect(url_for('logged', key=user, nif=newperson.nif))

    else:
        attempt = 'retry'
        return redirect(url_for('signUp', user=user, attempt=attempt))


'''
    This section is the one where products are managed. The screens related with
    products are managed here.    
'''


# Shows the home screen of the site for customers
@app.route('/<key>/<nif>')
def logged(key, nif):
    # If we need to clear the table:
    # db.session.query(Product).delete()

    # Refresh the inventory
    refreshProducts(IVA, maxQuantity)

    user = finder(key, nif)

    # Database collect
    if user.mail != 'admin' and key == 'customer':
        productList = db.session.query(Product).all()

        for i, product in enumerate(productList):
            if product.quantity <= 0:
                productList.pop(i)

    elif user.mail == 'admin':
        productList = db.session.query(Product).all()

    elif key == 'supplier':
        brand = user.name.capitalize()
        productList = db.session.query(Product).filter_by(brand=brand).all()
    print("All is going OK")


    return render_template("homePage.html", products=productList, key=key, user=user,
                           enumerate=enumerate, round=round, len=len)


# Shows a single product with more information
@app.route('/<key>/<nif>/<prodName>')
def product(key, nif, prodName):
    selectedProduct = finder('product', prodName)
    user = finder(key, nif)

    # print(customer)
    return render_template("productScreen.html", product=selectedProduct, user=user, key=key,
                           round=round, logged=False)


'''
    This section is the one where suppliers actions are managed. The screens related with
    supplier´s products are managed here.    
'''


# Screen to add info of a product to the supplier list
@app.route('/newProduct/<nif>')
def newProduct(nif):
    supplier = finder('supplier', nif)

    return render_template('productData.html', supplier=supplier, attempt='0', product=None)


# Add new product to the database
@app.route('/createNewProduct/<nif>/<attempt>', methods=['POST'])
def createNewProduct(nif, attempt):
    supplier = finder('supplier', nif)

    catchProduct(supplier, 'new')

    return redirect(url_for('logged', key='supplier', nif=supplier.nif))


# Edit a product on the database
@app.route('/editProduct/<nif>/<prodName>')
def editProduct(nif, prodName):
    selectedProduct = finder('product', prodName)
    supplier = finder('supplier', nif)

    return render_template('productData.html', supplier=supplier, attempt='edit', product=selectedProduct)


# Edit a product on the database
@app.route('/editedProduct/<nif>/<prodName>', methods=['POST'])
def editedProduct(nif, prodName):
    selectedProduct = finder('product', prodName)
    supplier = finder('supplier', nif)

    catchProduct(supplier, 'edit', selectedProduct)

    return redirect(url_for('logged', key='supplier', nif=supplier.nif))


# Add products when stock is out
@app.route('/addQuantity/<nif>/<prodName>', methods=['POST'])
def addStock(nif, prodName):
    selectedProduct = finder('product', prodName)
    supplier = finder('supplier', nif)

    if selectedProduct.quantity != seletedProduct.maximumQuantity:
        quantityAdded = int(request.form['addQuantity-' + selectedProduct.name])
        selectedProduct.quantity += quantityAdded
        selectedProduct.stock = (selectedProduct.quantity/selectedProduct.maximumQuantity)*100

        return redirect(url_for('logged', key='supplier', nif=supplier.nif))

    else:
        maxAdding = seletedProduct.maximumQuantity - selectedProduct.quantity

        return redirect(url_for('editProduct', nif=supplier.nif, prodName=selectedProduct.name, attempt='maxExceeded'))

'''
    This section is the one where shopping cart is managed. The screens related with
    shopping cart are managed here.    
'''


# Shopping cart
# We are going to use a CSV file to archive the shopping cart (Look at createCart in shoppingCart.py for
# more info)
@app.route('/ShoppingCart/<nif>')
def shoppingCart(nif):
    # Call to the complete customer info
    customer = finder('customer', nif)

    # let's decode the csv file where shopping cart is stored to a variable that jinja could use
    products = decodeCSV(customer)
    # print(products)

    return render_template('cart.html', customer=customer, products=products, range=range, round=round)


# Add product to cart
@app.route('/addToCart/<nif>/<prodName>')
def addToCart(nif, prodName):
    selectedProduct = finder('product', prodName)
    customer = finder('customer', nif)
    
    addNewProduct(customer, selectedProduct.name)

    return redirect(url_for("logged", key='customer', nif=customer.nif))


# Delete product from cart
@app.route('/deleteFromCart/<nif>/<prodName>')
def deleteFromCart(nif, prodName):
    selectedProduct = finder('product', prodName)
    customer = finder('customer', nif)

    deleteProduct(customer, selectedProduct.name)

    return redirect(url_for("shoppingCart", nif=customer.nif))


'''
    This section is where payments are managed. The actions related with
    payments were done here.    
'''


# Payment gateway
@app.route('/paymentGateway/<nif>', methods=['POST'])
def paymentGateway(nif):
    customer = finder('customer', nif)

    products, totalAmount = catchQuantity(customer)

    return render_template("payment.html", customer=customer, products=products, totalAmount=totalAmount,
                           range=range, round=round)


# Final page after payment
@app.route('/paymentDone/<nif>', methods=['POST'])
def paymentDone(nif):
    customer = finder('customer', nif)
    deleteCart(customer, maxQuantity)

    payMethod = request.form['payment']

    return render_template("paymentDone.html", customer=customer, payMethod=payMethod)


''' This is the starter of the application '''
if __name__ == '__main__':
    try:
        databasePath = '/database/database.db'
        database = open(databasePath, 'x')

    except:
        print("Database already exists")

    finally:
        db.Base.metadata.create_all(db.engine)  # Creates data model
        app.run(debug=True)  # Debug restart Flask server with every code change or model restart.
