from flask import Response, make_response, Request, request, session
from flask import render_template, flash, redirect, url_for
from application import application
from main import *

import json
import main
import etl
########################This starts the page renders#######################################

@application.route('/home', methods=['GET', 'POST'])
@application.route('/', methods=['GET', 'POST'])
def index():
    if "5000" in request.url:
        css = "../static/css/main.css"
        jquery_min = "../static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    else:
        css = "./static/css/mainQaret.css"
        jquery_min = "./static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    try:
        user = session['userID']
    except Exception as e:
        print("Error with user: {}".format(e.args))
        user = ""
        return redirect(url_for('login'))
    response = Response("")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    response.headers["Expires"] = "0" # Proxies.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response = make_response(render_template('index.html',
                                             title='Querc.org',
                                             css = css,
                                             jquery_min = jquery_min,
                                             icon = icon))
    return response

@application.route('/Login', methods=['GET'])
@application.route('/login', methods=['GET'])
def login():
    if "5000" in request.url:
        css = "../static/css/main.css"
        jquery_min = "../static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    else:
        css = "./static/css/mainQaret.css"
        jquery_min = "./static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    response = Response("")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    response.headers["Expires"] = "0" # Proxies.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response = make_response(render_template('login.html',
                                             title='Querc.org - Login',
                                             css = css,
                                             jquery_min = jquery_min,
                                             icon = icon))
    return response

@application.route('/Logout')
@application.route('/logout')
def logout():
    if "5000" in request.url:
        css = "../static/css/main.css"
        jquery_min = "../static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    else:
        css = "./static/css/mainQaret.css"
        jquery_min = "./static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    session.clear()
    return redirect(url_for('login'))
    response = Response("")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    response.headers["Expires"] = "0" # Proxies.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response = make_response(render_template('logout.html',
                                             title='Querc.org - Goodbye',
                                             css = css,
                                             jquery_min = jquery_min,
                                             icon = icon))
    return response

@application.route('/Catalog', methods=['GET', 'POST'])
@application.route('/catalog', methods=['GET', 'POST'])
def catalog():
    if "5000" in request.url:
        css = "../static/css/main.css"
        jquery_min = "../static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    else:
        css = "./static/css/mainQaret.css"
        jquery_min = "./static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    response = Response("")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    response.headers["Expires"] = "0" # Proxies.
    response.headers['Access-Control-Allow-Origin'] = '*'
    dataSet = json.dumps(main.get_catalog())
    #allows people to view the catalog while not signed in. But wont let them add to the shopping cart. 
    if "userID" in session:
        add_to_cart = ""
    else:
        add_to_cart = "disabled"
    response = make_response(render_template('catalog.html',
                                             title='Querc.org - Catalog',
                                             css = css,
                                             jquery_min = jquery_min,
                                             icon = icon,
                                             add_to_cart = add_to_cart,
                                             dataSet = dataSet))
    return response

@application.route('/Cart', methods=['GET', 'POST'])
@application.route('/cart', methods=['GET', 'POST'])
def cart():
    if "5000" in request.url:
        css = "../static/css/main.css"
        jquery_min = "../static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    else:
        css = "./static/css/mainQaret.css"
        jquery_min = "./static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    try:
        user = session['userID']
    except Exception as e:
        print("Error with user: {}".format(e.args))
        user = ""
        return redirect(url_for('login'))
    response = Response("")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    response.headers["Expires"] = "0" # Proxies.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response = make_response(render_template('shopping_cart.html',
                                             title='Querc.org - Cart',
                                             css = css,
                                             jquery_min = jquery_min,
                                             icon = icon))
    return response

@application.route('/Dashboards', methods=['GET', 'POST'])
@application.route('/dashboards', methods=['GET', 'POST'])
def dashboards():
    if "5000" in request.url:
        css = "../static/css/main.css"
        jquery_min = "../static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    else:
        css = "./static/css/mainQaret.css"
        jquery_min = "./static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    try:
        adminUserID = session['adminUserID']
        adminUser = session['adminUser']
    except Exception as e:
        print("Error with user: {}".format(e.args))
        user = ""
        return redirect(url_for('Admin'))
    response = Response("")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    response.headers["Expires"] = "0" # Proxies.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response = make_response(render_template('admin_dashboard.html',
                                             title='Querc.org - Admin - Dashboard',
                                             css = css,
                                             jquery_min = jquery_min,
                                             icon = icon))
    return response

@application.route('/Reports', methods=['GET', 'POST'])
@application.route('/Reports', methods=['GET', 'POST'])
def reports():
    if "5000" in request.url:
        css = "../static/css/main.css"
        jquery_min = "../static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    else:
        css = "./static/css/mainQaret.css"
        jquery_min = "./static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    try:
        adminUserID = session['adminUserID']
        adminUser = session['adminUser']
    except Exception as e:
        print("Error with user: {}".format(e.args))
        user = ""
        return redirect(url_for('Admin'))
    response = Response("")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    response.headers["Expires"] = "0" # Proxies.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response = make_response(render_template('reporting.html',
                                             title='Querc.org - Admin - User Search',
                                             css = css,
                                             jquery_min = jquery_min,
                                             icon = icon))
    return response

@application.route('/Transactions', methods=['GET', 'POST'])
@application.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if "5000" in request.url:
        css = "../static/css/main.css"
        jquery_min = "../static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    else:
        css = "./static/css/mainQaret.css"
        jquery_min = "./static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    try:
        adminUserID = session['adminUserID']
        adminUser = session['adminUser']
    except Exception as e:
        print("Error with user: {}".format(e.args))
        user = ""
        return redirect(url_for('Admin'))
    response = Response("")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    response.headers["Expires"] = "0" # Proxies.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response = make_response(render_template('transactions.html',
                             title='Querc.org - Admin - Transactions',
                             css=css,
                             jquery_min=jquery_min,
                             icon=icon))
    return response

@application.route('/Admin')
@application.route('/admin')
def admin():
    if "5000" in request.url:
        css = "../static/css/main.css"
        jquery_min = "../static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    else:
        css = "./static/css/mainQaret.css"
        jquery_min = "./static/js/jquery-ui.min.js"
        icon = "./static/images/favicon.png"
    response = Response("")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    response.headers["Expires"] = "0" # Proxies.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response = make_response(render_template('admin_login.html',
                                             title='Querc.org - Login Admin',
                                             css = css,
                                             jquery_min = jquery_min,
                                             icon = icon))
    return response

#####################This starts the Ajax Requests###################################################

#called by eventing
@application.route('/refreshCatalog', methods=['POST', 'GET'])
def refreshCatalog():
    try:
        result = main.refresh_catalog()
        return json.dumps({}), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}


@application.route('/Login', methods=['POST'])
@application.route('/login', methods=['POST'])
def agentLogin():
    try:
        session.clear()
        url = request.form['url']
        user = request.form['userID']
        password = request.form['password']
        result = main.do_login(user, password)
        print(result)
        login = {}
        if "active" in result:
            if result['active'] == True:
                login['active'] = result['active']
                login['success'] = True
                login['userID'] = request.form['userID']
                login['error'] = None
            elif result['active'] == False:
                login['active'] = result['active']
                login['success'] = False
                login['userID'] = request.form['userID']
                login['error'] = "Inactive account. Please contact the admin"
        else:
            login['active'] = False
            login['success'] = False
            login['userID'] = request.form['userID']
            login['error'] = "Incorrect username or password"
        if login['active'] == True:
            session['userID'] = login['userID']
            session['cbDocID'] = result['id']
        return json.dumps(login), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        login = {}
        login['success'] = False
        login['error'] = "Unknown Error: {}".format(e)
        return json.dumps(login), 200, {'ContentType':'application/json'}

@application.route('/adminLogin', methods=['POST'])
def adminLogin():
    try:
        session.clear()
        url = request.form['url']
        user = request.form['userID']
        password = request.form['password']
        result = main.do_admin_login(user, password)
        print(result)
        login = {}
        if result == True:
            session['adminUserID'] = user
            session['adminUser'] = True
            login['success'] = True
        else:
            login['success'] = False
            login['error'] = "Username or Password incorrect"
        return json.dumps(login), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        login = {}
        login['success'] = False
        login['error'] = "Unknown Error: {}".format(e)
        return json.dumps(login), 200, {'ContentType':'application/json'}
    
@application.route('/getUserProfile', methods=['POST'])
def getUserProfile():
    try:
        print(session['cbDocID'])
        result = main.getUserProfile(session['cbDocID'])
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}
    
@application.route('/getAddress', methods=['POST'])
def getAddress():
    try:
        address_name = request.form['name']
        result = main.getAddress(session['cbDocID'], address_name)
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}
    
@application.route('/getCC', methods=['POST'])
def getCC():
    try:
        cc_name = request.form['name']
        result = main.getCC(session['cbDocID'], cc_name)
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}
    
@application.route('/getCatalog', methods=['POST'])
def getCatalog():
    try:
        result = main.get_catalog()
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}

@application.route('/updateCart', methods=['POST'])
def updateCart():
    try:
        rows = []
        data = json.loads(request.data)
        for row in data['rows']:
            catagory = row['category']
            sku = row['sku']
            list_price = row['list_price']
            sale_price = row['sale_price']
            brand = row['brand']
            name_title = row['name_title']
            uniq_id = row['uniq_id']
            success = main.add_to_cart(session['cbDocID'], session['userID'], sku, sale_price, 1, name_title)
        return json.dumps({}), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}
    
@application.route('/getCart', methods=['POST'])
def getCart():
    try:
        result = main.get_cart(session['cbDocID'], session['userID'])
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}

@application.route('/purchaseCart', methods=['POST'])
def purchaseCart():
    try:
        rows = []
        data = json.loads(request.data)
        for row in data['rows']:
            category = row['category']
            sku = row['sku']
            price = row['sale_price']
            brand = row['brand']
            name_title = row['name_title']
            quantity = row['qty']
            #potentially add code to update qty?
        success = main.purchase_cart(session['cbDocID'], session['userID'])
        return json.dumps(success), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}
    
@application.route('/getOrders', methods=['POST'])
def getOrders():
    try:
        result = main.get_orders(session['cbDocID'], session['userID'])
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}

@application.route('/getCartItems', methods=['POST'])
def getCartItems():
    try:
        try:
            result = main.getCartItems()
        except Exception as e:
            print(e)
            result = main.get_cart_items()
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}

@application.route('/getClosedItems', methods=['POST'])
def getClosedItems():
    try:
        print(request.form)
        startDate = request.form['dateFrom']
        endDate = request.form['dateTo']
        try:
            result = main.getClosedItems(startDate, endDate)
        except Exception as e:
            print(e)
            result = main.get_closed_items(startDate, endDate)
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}

#Tries to use the analytics service first to get totals if that fails defaults 
#to n1ql
@application.route('/getTxnTotal', methods=['POST'])
def getTxnTotal():
    try:
        print(request.form)
        startDate = request.form['dateFrom']
        endDate = request.form['dateTo']
        try:
            result = main.getClosedSalesTotals(startDate, endDate)
        except:
            result = main.get_txn_total(startDate, endDate)
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}

#Tries to use the analytics service first to get totals if that fails defaults 
#to n1ql
@application.route('/getCartTotal', methods=['POST'])
def getCartTotal():
    try:
        try:
            result = main.getShoppingCartTotals()
        except:
            result = main.get_cart_total()
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}

@application.route('/getUserList', methods=['POST'])
def getUserList():
    try:
        print(request.form)
        street1 = request.form['street1']
        street2 = request.form['street2']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']
        
        result = main.query_by_address(street1, street2, city, state, zipcode)
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}

@application.route('/getAdminTxnList', methods=['POST'])
def getAdminTxnList():
    try:
        print(request.form.to_dict())
        
        result = main.get_admin_txn_list(request.form.to_dict())
        return json.dumps(result), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({}), 200, {'ContentType':'application/json'}

@application.route('/createShoppingCarts', methods=['POST'])
def createShoppingCarts():
    try:
        result = etl.generateShoppingCarts()
        if result == True:
            return json.dumps({"status":"success"}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({"status":"failed"}), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({"status":"failed"}), 200, {'ContentType':'application/json'}
    
@application.route('/createTransactions', methods=['POST'])
def createTransactions():
    try:
        result = etl.generateTxnFromCarts()
        if result == True:
            return json.dumps({"status":"success"}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({"status":"failed"}), 200, {'ContentType':'application/json'}
    except Exception as e:
        print("Unknown error: {}".format(e))
        return json.dumps({"status":"failed"}), 200, {'ContentType':'application/json'}

@application.route("/updateUserProfile", methods=['POST'])
def updateUserProfile():
    print(request.form.to_dict())
    status = update_user_profile(request.form.to_dict())
    if status == True:
        return json.dumps({"status":"success"}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({"status":"failed"}), 200, {'ContentType':'application/json'}
    
@application.route("/addCC", methods=['POST'])
def addCC():
    result = main.add_cc(session['cbDocID'], request.form.to_dict())
    return json.dumps({"status":"success"}), 200, {'ContentType':'application/json'}

@application.route("/deleteCC", methods=['POST'])
def deleteCC():
    result = main.delete_cc(session['cbDocID'], request.form.to_dict())
    return json.dumps({"status":"success"}), 200, {'ContentType':'application/json'}

@application.route("/saveCC", methods=['POST'])
def saveCC():
    result = main.save_cc(session['cbDocID'], request.form.to_dict())
    return json.dumps({"status":"success"}), 200, {'ContentType':'application/json'}

@application.route("/addAddress", methods=['POST'])
def addAddress():
    result = main.add_address(session['cbDocID'], request.form.to_dict())
    return json.dumps({"status":"success"}), 200, {'ContentType':'application/json'}

@application.route("/deleteAddress", methods=['POST'])
def deleteAddress():
    result = main.delete_address(session['cbDocID'],request.form.to_dict())
    return json.dumps({"status":"success"}), 200, {'ContentType':'application/json'}

@application.route("/saveAddress", methods=['POST'])
def saveAddress():
    result = main.save_address(session['cbDocID'], request.form.to_dict())
    return json.dumps({"status":"success"}), 200, {'ContentType':'application/json'}