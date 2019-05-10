# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "tdenton"
__date__ = "$Apr 27, 2019 2:13:15 PM$"

import def_couchbase
import csv
import json
import random
global instance
import datetime
import time
from datetime import timedelta

def gt(dt_str):
     dt, _, us= dt_str.partition(".")
     dt= datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
     us= int(us.rstrip("Z"), 10)
     return dt + datetime.timedelta(microseconds=us)

def random_date(start, end):
    int_delta = int((end - start).total_seconds())
    random_second = random.randrange(int_delta)
    return (start + timedelta(seconds=random_second)).isoformat()

def getUsers():
    instance = get_couchbase()
    
    query = "select meta().id from `main` where jsonType='user';"
    users = []
    results = instance.main.n1ql_query(query)
    for row in results:
        users.append(row['id'])
    user_length = len(users)
    return users, user_length

def getProducts():
    instance = get_couchbase()
    
    query = "select meta().id from `main` where jsonType='product' and sale_price != '' and name_title != '';"
    products = []
    results = instance.main.n1ql_query(query)
    for row in results:
        products.append(row['id'])
    product_length = len(products)
    return products, product_length

def getShoppingCarts():
    instance = get_couchbase()
    query = "select meta().id from `main` where jsonType='shoppingCart';"
    carts = []
    results = instance.main.n1ql_query(query)
    for cart in results:
        carts.append(cart['id'])
    cart_length = len(carts)
    return carts, cart_length


def generateShoppingCarts():
    try:
        instance = get_couchbase()
        users, user_length = getUsers()
        products, product_length = getProducts()

        for x in range(0, 100):
            userID = users[random.randint(0, user_length-1)]
            numProducts = random.randint(0,15)
            productList = []
            for x in range(0, numProducts):
                productList.append(products[random.randint(0, product_length-1)])

            print(userID, productList)
            userName = instance.main.get(userID).value['email']
            docID = "{}_cart".format(userID)
            document = {}
            document['created_date'] = random_date(datetime.datetime.now()-datetime.timedelta(days=356), datetime.datetime.now())   
            document['item_list'] = []
            extended_cost = 0
            num_items = 0
            for product in productList:
                cbProduct = instance.main.get(product).value
                productSubDoc = {}
                productSubDoc['id'] = product
                productSubDoc['price'] = float(cbProduct['sale_price'])
                productSubDoc['qty'] = random.randint(1,10)
                productSubDoc['name_title'] = cbProduct['name_title']
                num_items += productSubDoc['qty']
                extended_cost += productSubDoc['price'] * productSubDoc['qty']
                document['item_list'].append(productSubDoc)
            document['num_items'] = num_items
            document['extended_cost'] = extended_cost
            document['jsonType'] = "shoppingCart"
            document['updated_date'] = random_date(gt(document['created_date']), datetime.datetime.now())   
            document['parent'] = userID
            document['userName'] = userName
            document['docID'] = docID
            instance.main.upsert(docID, document)
        return True
    except Exception as e:
        print(e)
        return False

def generateTxnFromCarts():
    try:
        instance = get_couchbase()
        carts, cart_length = getShoppingCarts()
        y = cart_length
        for x in range(0, min(50, cart_length)):
            y = y - 1
            cartID = carts.pop(random.randint(0,y))

            cartDoc = instance.main.get(cartID).value
            userID = cartDoc['parent']
            userDoc = instance.main.get(userID).value

            txnDocument = {}
            txnDocument['billing_address'] = userDoc['billing_address']
            for cc in userDoc['creditCards']:
                if cc['active'] == True:
                    txnDocument['creditCard']=cc
                    break
            txnDocument['extended_cost'] = cartDoc['extended_cost']
            txnDocument['first_name'] = userDoc['first_name']
            txnDocument['last_name'] = userDoc['last_name']
            txnDocument['item_list'] = []
            for item in cartDoc['item_list']:
                itemDoc = {}
                itemCB = instance.main.get(item['id']).value
                itemDoc['category'] = itemCB['category']
                itemDoc['sku'] = itemCB['sku']
                itemDoc['brand'] = itemCB['brand']
                itemDoc['name_title'] = itemCB['name_title']
                itemDoc['qty'] = item['qty']
                itemDoc['sale_price'] = item['price']
                txnDocument['item_list'].append(itemDoc)
            txnDocument['jsonType'] = "Transaction"
            txnDocument['purchase_date'] = random_date(gt(cartDoc['updated_date']), datetime.datetime.now()) 
            for address in userDoc['shipping_address']:
                if address['active'] == True:
                    txnDocument['shipping_address']=address
                    break
            txnDocument['uniqueID'] = userDoc['userID']
            txnDocument['userID'] = userDoc['email']
            docID = "{}_{}_txn".format(txnDocument['uniqueID'], txnDocument['purchase_date'])

            instance.main.upsert(docID, txnDocument)
            instance.main.delete(cartID)
        return True
    except Exception as e:
        print(e)
        return False

def createLoad():
    generateShoppingCarts()
    generateTxnFromCarts()
    

def generateCC():
    result = {}
    result['active']= True
    result['ccNum'] = random.randint(4000000000000000, 5999999999999999)
    startdate = datetime.datetime.now()
    _date = startdate+datetime.timedelta(random.randint(1, 365*5))
    result['date'] = datetime.datetime(_date.year, _date.month, _date.day).isoformat()
    if str(result['ccNum'])[0] == '4':
        result['name'] = "Visa_{}".format(str(result['ccNum'])[-4:])
        result['cid'] = random.randint(100, 999)
    elif str(result['ccNum'])[0] == '5':
        result['name'] = "Mastercard_{}".format(str(result['ccNum'])[-4:])
        result['cid'] = random.randint(1000, 9999)
    return result
    

def get_couchbase():
    try:
        instance.main.connected
        return instance
    except Exception as e:
        instance = def_couchbase.auth_cb_cluster()
        return instance

def create_catalog():
    instance = get_couchbase()
    
    file_name = "./static/resources/jcpenney_com-ecommerce_sample.csv"
    with open(file_name) as csvfile:
        freader = csv.DictReader(csvfile, delimiter=",", quotechar="\"")
        for row in freader:
            try:
                docID = "{}".format(row['sku'])
                message = row
                float(message['list_price'])
                float(message['sale_price']) 
                message['Reviews']= None
                message['jsonType'] = "product"
                instance.main.upsert(docID, message)
            except:
                pass

def create_users():
    instance = get_couchbase()
    
    file_name = "./static/resources/us-500.csv"
    with open(file_name) as csvfile:
        freader = csv.DictReader(csvfile, delimiter=",", quotechar="\"")
        for row in freader:
            try:
                docID = "{}".format(hash(json.dumps({"first_name": row['first_name'], 
                                                    "last_name": row['last_name'],
                                                    "email": row['email']})))
                message = {}
                message['userID'] = docID
                billing_address = {}
                billing_address['street1'] = row['address']
                billing_address['street2'] = None
                billing_address['city'] = row['city']
#                billing_address['county'] = row['county']
                billing_address['state'] = row['state']
                billing_address['zipcode'] = row['zip']
                message['billing_address'] = billing_address
                
                shipping_address = billing_address.copy()
                shipping_address['active'] = True
                shipping_address['name'] = billing_address['street1']
                shipping_addresses = []
                shipping_addresses.append(shipping_address)
                
                message['shipping_address'] = shipping_addresses
                message['first_name'] = row['first_name']
                message['last_name'] = row['last_name']
                message['web'] = row['web']
                message['phone1'] = row['phone1']
                message['phone2'] = row['phone2']
                message['company_name'] = row['company_name']
                message['active'] = True
                message['email'] = row['email']
                message['jsonType'] = "user"
                message['pw'] = row['first_name']
                message['creditCards'] = []
                message['creditCards'].append(generateCC())
                print(message)
                instance.main.upsert(docID, message)
#                Query to remove county if necessary
#                update `main`
#                unset c.county for c in shipping_address end, 
#                billing_address.county
#                where jsonType="user";
            except Exception as e:
                print("error: {}".format(e))
                

if __name__ == "__main__":
#    create_catalog()
    create_users()
