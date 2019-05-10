# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "tdenton"
__date__ = "$Apr 27, 2019 11:29:07 AM$"

import def_couchbase
import datetime

from couchbase.analytics import AnalyticsQuery

import json
global instance

def get_couchbase():
    try:
        instance.main.connected
        return instance
    except Exception as e:
        instance = def_couchbase.auth_cb_cluster()
        return instance

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def gt(dt_str):
    print(dt_str)
    dt, _, us= dt_str.partition(".")
    dt= datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    return dt
 
###############################################################
#######################KV Queries##############################
###############################################################

#Uses bucket operations to get addresse
def getAddress(cbDocID, address_name):
    try:
        instance = get_couchbase()
        document = instance.main.get(cbDocID)
        result = {}
        for address in document.value['shipping_address']:
            if address['name'] == address_name:
                result = address
        return result
    except Exception as e:
        print(e)
        return({})

#Uses bucket operations to get Credit Card info. 
#Credit card numbers should be encrypted. This is where the CC could be decrypted
def getCC(cbDocID, CC_name):
    try:
        instance = get_couchbase()
        document = instance.main.get(cbDocID)
        result = {}
        for cc in document.value['creditCards']:
            if cc['name'] == CC_name:
                result = cc
        print(result)
        return result
    except Exception as e:
        print(e)
        return({})

#returns a user profile by docID using kv operations
#since we dont set an address name in the import of user profiles, this assigns
#a name to populate a dropdown in the UI
def getUserProfile(cbDocID):
    try:
        instance = get_couchbase()
        document = instance.main.get(cbDocID)
        address_names = []
        for addresses in document.value['shipping_address']:
            address_names.append(addresses['name'])
        document.value['address_names'] = address_names
        return document.value
    except Exception as e:
        print(e)
        return({})

#adds items to a shopping cart
def add_to_cart(cbDocID, userID, uniq_id, sale_price, qty, name_title):
    instance = get_couchbase()
    DocID = "{}_cart".format(cbDocID)
    extended_cost = 0
        
    #This checks to see if the document already exists. If it doesnt it creates it
    try:
        result = instance.main.get(DocID)
        document = result.value
        document['updated_date'] = datetime.datetime.now().isoformat()
        
        #checks to see if an item is already in a shopping cart. 
        #Duplicate Items are not allowed
        if len([item for item in document['item_list'] if item['id'] == uniq_id]) > 0:
            print("Repeat item listed")
        else:
            document['item_list'].append({"id": uniq_id, "price":float(sale_price), "qty":qty, "name_title":name_title})
        document['num_items'] = len(document['item_list'])
        document['jsonType'] = "shoppingCart"
    except Exception as e:
        print(e)
        document = {}
        document['DocID'] = DocID
        document['parent'] = cbDocID
        document['userName'] = userID
        document['created_date'] = datetime.datetime.now().isoformat()
        document['updated_date'] = datetime.datetime.now().isoformat()
        document['item_list'] = []
        document['item_list'].append({"id": uniq_id, "price":float(sale_price), "qty":qty, "name_title":name_title})
        document['num_items'] = len(document['item_list'])
        document['jsonType'] = "shoppingCart"
    
    #calculates the extended cost of the entire shopping cart.
    for item in document['item_list']:
        extended_cost += item['qty']+item['price']
    document['extended_cost'] = extended_cost
    
    # create/upsert the new doc
    try:
        instance.main.upsert(DocID, document, persist_to=1)
        return True
    except Exception as e:
        print("Error upserting document: {}".format(e))
        return False

#gets the shopping cart to be displayed in a JquereyUI Datatable
def get_cart(cbDocID, userID):
    try:
        instance = get_couchbase()
        cart_doc = instance.main.get("{}_cart".format(cbDocID)).value
        items = []
        for item in cart_doc['item_list']:
            item_dict = {}
            temp_doc = instance.main.get(item['id']).value
            #column names in the table
            item_dict['brand'] = temp_doc['brand']
            item_dict['category'] = temp_doc['category']
            item_dict['name_title'] = item['name_title']
            item_dict['sale_price'] = item['price']
            item_dict['sku'] = temp_doc['sku']
            item_dict['qty'] = item['qty']
            items.append(item_dict)
        finalReturn = {}
        finalReturn['iTotalRecords'] = len(items)
        finalReturn['iTotalDisplayRecords'] = len(items)
        finalReturn['aaData'] = items
        return(finalReturn)
    except Exception as e:
        #if the table is empty this prevents the table from looking like it is still trying to load data
        print(e)
        finalReturn = {}
        finalReturn['iTotalRecords'] = 0
        finalReturn['iTotalDisplayRecords'] = 0
        finalReturn['aaData'] = {}
        return(finalReturn)

#This converts the shopping cart into a transaction
def purchase_cart(cbDocID, userID):
    instance = get_couchbase()
    
    #gets the user profile and shopping cart to be converted
    cart_doc = instance.main.get("{}_cart".format(cbDocID)).value
    userDoc = instance.main.get("{}".format(cbDocID)).value
    
    #starts to create the transaction document
    document = {}
    docID = "{}_{}_txn".format(cbDocID, datetime.datetime.now().isoformat())
    document['uniqueID'] = cbDocID
    document['userID'] = userDoc['email']
    document['extended_cost'] = cart_doc['extended_cost']
    
    items = []
    #goes through each item in the list on the shopping cart and gets its product document
    #then it takes the data it needs and adds it to the transaction document
    for item in cart_doc['item_list']:
        item_dict = {}
        temp_doc = instance.main.get(item['id']).value
        item_dict['brand'] = temp_doc['brand']
        item_dict['category'] = temp_doc['category']
        item_dict['name_title'] = item['name_title']
        item_dict['sale_price'] = item['price']
        item_dict['sku'] = temp_doc['sku']
        item_dict['qty'] = item['qty']
        items.append(item_dict)
    document['item_list'] = items
    document['billing_address'] = userDoc['billing_address']
    #gets the active shipping address
    document['shipping_address'] = [address for address in userDoc['shipping_address'] if address['active'] == True][0]
    #gets the active CC
    document['creditCard'] = [creditCard for creditCard in userDoc['creditCards'] if creditCard['active'] == True][0]
    #sets the purchase date in ISO format
    document['purchase_date'] = datetime.datetime.now().isoformat()
    document['first_name'] = userDoc['first_name']
    document['last_name'] = userDoc['last_name']
    document['jsonType'] = "Transaction"
    
    #Attempts to upsert the transaction
    try:
        instance.main.upsert(docID, document, persist_to=1)
        try:
            #Looks to see if the upsert was successful. If it was it deletes the shopping cart. if not it reports an error. 
            instance.main.get(docID)
            instance.main.delete(cart_doc['DocID'])
            return {"status": "success"}
        except Exception as e:
            print(e)
            return {"status": "failed"}
    except Exception as e:
        print(e)
        return {"status": "failed"}

#Simple way to handle admin login. Not secure. not the right way to do things. 
def do_admin_login(userID, password): # this is definitely not the right way to do things. Will work for the demo to show workflow
    if userID == "tdenton" and password == password:
        return True
    else:
        return False

###############################################################
#########################N1QL Queries############################
###############################################################

#Query by address as requested. Unnests the address documents from the user profiles. 
#Tried with array query but unnest performed better. 
#Considered a reverse lookup of user profiles by making addresses their own 
#document and querying address docs and doing a join to the user profile based 
#on an array of doc IDs. Chose not to for this data model but would probably do 
#that if addresses were the primary data and we needed to query for geospatial 
#boundaries, or we had many many users at the same address. 
def query_by_address(street1, street2, city, state, zip):
    try:
        instance = get_couchbase()
        query = '''select users.first_name,
                                users.last_name,
                                users.email,
                                addresses.street1,
                                addresses.street2,
                                addresses.city,
                                addresses.state,
                                addresses.zipcode
                                from `main` users
                                UNNEST(users.shipping_address) as addresses
                                where users.jsonType="user"
                                and (addresses.street1 LIKE "%{}%" or users.billing_address.street1 LIKE "%{}%")
                                and (addresses.street2 LIKE "%{}%" or users.billing_address.street2 LIKE "%{}%" or addresses.street2 is null or users.billing_address.street2 is null)
                                and (addresses.city LIKE "%{}%" or users.billing_address.city LIKE "%{}%" or addresses.city is null or users.billing_address.city is null)
                                and (addresses.zipcode LIKE "%{}%" or users.billing_address.zipcode LIKE "%{}%" or addresses.zipcode is null or users.billing_address.zipcode is null)
                                and (addresses.state LIKE "%{}%" or users.billing_address.state LIKE "%{}%" or addresses.state is null or users.billing_address.state is null)
                                and addresses.active = true;'''.format(street1, street1,
                                                                        street2, street2,
                                                                        city, city,
                                                                        zip, zip,
                                                                        state, state)
        result = instance.main.n1ql_query(query)
        results = []
        
        #creates the results for the display table
        for user in result:
            record = {}
            record['first_name'] = user['first_name']
            record['last_name'] = user['first_name']
            record['email'] = user['email']
            if user['street2'] is None:
                user['street2'] = ""
            record['address'] = "{} {} {} {} {}".format(user['street1'], 
                                                                    user['street2'],
                                                                    user['city'],
                                                                    user['state'],
                                                                    user['zipcode'])
            results.append(record)
        finalReturn = {}
        finalReturn['iTotalRecords'] = len(results)
        finalReturn['iTotalDisplayRecords'] = len(results)
        finalReturn['aaData'] = results
        return(finalReturn)
    except Exception as e:
        print(e)
        finalReturn = {}
        finalReturn['iTotalRecords'] = 0
        finalReturn['iTotalDisplayRecords'] = 0
        finalReturn['aaData'] = {}
        return(finalReturn)

def get_admin_txn_list(request):
    if request['dollarFrom'] == "":
        request['dollarFrom'] = 0
    if request['dollarTo'] == "":
        request['dollarTo'] = 1000000000000000000000000000000000000000000
    if request['name'] != "":
       request['name'] = request['name'].lower() 
    if request['address'] != "":
        request['address'] = request['address'].lower()
    try:
        instance = get_couchbase()
        query = '''select * 
                    from `main` txn
                    where jsonType = 'Transaction'
                    and STR_TO_MILLIS(SUBSTR(txn.purchase_date, 0, LENGTH(txn.purchase_date)-3)) between STR_TO_MILLIS('{}') and STR_TO_MILLIS('{}')
                    and txn.extended_cost between {} and {}
                    and lower(first_name) || " " || lower(last_name) like "%{}%"
                    and lower(shipping_address.street1) || " " || lower(shipping_address.city) || " " || lower(shipping_address.state) || " " || lower(shipping_address.zipcode) like "%{}%";'''.format(request['dateFrom'], 
                                                                        request['dateTo'],
                                                                        request['dollarFrom'],
                                                                        request['dollarTo'],
                                                                        request['name'],
                                                                        request['address'])
        print(query)

                                                                                
        result = instance.main.n1ql_query(query)
        results = []
        
        #creates the results for the display table
        for txn in result:
            record = {}
            record['name'] = "{} {}".format(txn['txn']['first_name'], txn['txn']['last_name'])
            record['date'] = txn['txn']['purchase_date']
            record['amount'] = txn['txn']['extended_cost']
            if txn['txn']['shipping_address']['street2'] is None:
                txn['txn']['shipping_address']['street2'] = ""
            record['address'] = "{} {} {} {} {}".format(txn['txn']['shipping_address']['street1'], 
                                                                    txn['txn']['shipping_address']['street2'],
                                                                    txn['txn']['shipping_address']['city'],
                                                                    txn['txn']['shipping_address']['state'],
                                                                    txn['txn']['shipping_address']['zipcode'])
            results.append(record)
        finalReturn = {}
        finalReturn['iTotalRecords'] = len(results)
        finalReturn['iTotalDisplayRecords'] = len(results)
        finalReturn['aaData'] = results
        return(finalReturn)
    except Exception as e:
        print(e)
        finalReturn = {}
        finalReturn['iTotalRecords'] = 0
        finalReturn['iTotalDisplayRecords'] = 0
        finalReturn['aaData'] = {}
        return(finalReturn)

# this is not the right way to do things. Will work for the demo to show workflow
def do_login(email, password): 
    try:
        instance = get_couchbase()
        query = "select meta().id as id, active from `main` where jsonType='user' and email='{}' and pw = '{}'".format(email, password)
        result = instance.main.n1ql_query(query).get_single_result()
        if type(result) == dict:
            return result
        else:
            return {}
    except Exception as e:
        print(e)
        return({})

#To try and increase performance (decrease load time), and demonstrate eventing, 
#I have moved the query for the catalog to an on disk document. This will 
#prevent multiple users from trying to refresh the doc at the same time and 
#putting to much load on the system. This document is updated whenever a product 
#is updated based on the eventing service in couchbase. (Didnt make it any 
#faster, load time is based on rendering in the table not time to query)
def get_catalog():
    catalog_json = {}
    try:
        with open('/opt/cbdemo/src/application/static/resources/catalog_array.json', 'rb+') as infile:  
                catalog_json=json.loads(infile.read())
        return(catalog_json)
    except Exception as e:
        print(e)
        return catalog_json

#This is the function called whenever a product is updated. It recreates the catalog
def refresh_catalog():
    try:
        instance = get_couchbase()
        query_string = "select brand, category, list_price, name_title, sale_price, sku, uniq_id from `main` where jsonType='product';"
        query = instance.main.n1ql_query(query_string)
        results = []
        for row in query:
            if "" in row.values():
                pass
            else:
                results.append(row)
        with open('/opt/cbdemo/src/application/static/resources/catalog_array.json', 'w') as outfile:  
            json.dump(results, outfile)
    except Exception as e:
        print(e)
        return({})

#This queries the transactions that have been created for a specific user. 
def get_orders(cbDocID, userID):
    try:
        instance = get_couchbase()
        query_string = "select * from `main` where jsonType='Transaction' and uniqueID = '{}';".format(cbDocID)
        query = instance.main.n1ql_query(query_string)
        results = []
        for row in query:
            result = {}
            result['order_date'] = row['main']['purchase_date']
            result['amount'] = row['main']['extended_cost']
            result['card_name'] = row['main']['creditCard']['name']
            result['bill_location'] = row['main']['billing_address']['street1']
            result['ship_location'] = row['main']['shipping_address']['name']
            results.append(result)
        finalReturn = {}
        finalReturn['iTotalRecords'] = len(results)
        finalReturn['iTotalDisplayRecords'] = len(results)
        finalReturn['aaData'] = results
        return(finalReturn)
    except Exception as e:
        print(e)
        finalReturn = {}
        finalReturn['iTotalRecords'] = 0
        finalReturn['iTotalDisplayRecords'] = 0
        finalReturn['aaData'] = {}
        return(finalReturn)

#Gets the total amount of the transactions 
#based on a time period. 
def get_txn_total(startDate, endDate):
    try:
        instance = get_couchbase()
        query_string = '''select sum(extended_cost) total_cost
                        from `main` txn
                        where jsonType="Transaction" 
                        and STR_TO_MILLIS(SUBSTR(txn.purchase_date, 0, LENGTH(txn.purchase_date)-3)) between STR_TO_MILLIS('{}') and STR_TO_MILLIS('{}')
                        limit 1;'''.format(startDate, endDate)
        result = instance.main.n1ql_query(query_string).get_single_result()
        return result
    except Exception as e:
        print(e)
        return({})

#Gets the total value of the shopping carts. 
def get_cart_total():
    try:
        instance = get_couchbase()
        query_string = '''select sum(extended_cost) total_cost
                        from `main` txn
                        where jsonType="shoppingCart" 
                        limit 1;'''
        result = instance.main.n1ql_query(query_string).get_single_result()
        return result
    except Exception as e:
        print(e)
        return({})

#updates the user profile except for shipping addresses and credit card info
def update_user_profile(profile):
    try:
        instance = get_couchbase()
        query_string = '''update `main`
                            use keys '{}'
                            set first_name = '{}',
                            last_name = '{}',
                            email = '{}',
                            phone1 = '{}',
                            phone2 = '{}',
                            pw = '{}',
                            billing_address.street1 = '{}',
                            billing_address.street2 = '{}',
                            billing_address.city = '{}',
                            billing_address.state = '{}',
                            billing_address.zipcode = '{}'
                            '''.format(profile['userID'],
                                        profile['first_name'],
                                        profile['last_name'],
                                        profile['email'],
                                        profile['phone1'],
                                        profile['phone2'],
                                        profile['password'],
                                        profile['bill_street1'],
                                        profile['bill_street2'],
                                        profile['bill_city'],
                                        profile['bill_state'],
                                        profile['bill_zipcode'])
        print(query_string)
        instance.main.n1ql_query(query_string).execute()
        return True
    except Exception as e:
        print(e)
        return False
    
#Gets all of the shopping carts and puts the carts in a table format. 
def get_cart_items():
    try:
        instance = get_couchbase()
        query = '''SELECT items.name_title, items.price, items.id, sum(items.qty) as ordered 
                    FROM `main` carts 
                    UNNEST carts.item_list AS items  
                    where carts.jsonType='shoppingCart'
                    group by items.sku, items.id, items.price, items.name_title
                    order by sum(items.qty) desc
                    limit 50;'''
        query = instance.main.n1ql_query(query)
        results = []
        for row in query:
            results.append(x)
        finalReturn = {}
        finalReturn['iTotalRecords'] = len(results)
        finalReturn['iTotalDisplayRecords'] = len(results)
        finalReturn['aaData'] = results
        return  finalReturn
    except Exception as e:
        print(e)
        finalReturn = {}
        finalReturn['iTotalRecords'] = 0
        finalReturn['iTotalDisplayRecords'] = 0
        finalReturn['aaData'] = {}
        return(finalReturn)
    
#Gets all of the transactions for a time period and presents in a table format.
def get_closed_items(startDate, endDate):
    try:
        instance = get_couchbase()
        query = '''SELECT items.sku, items.sale_price, items.name_title, items.sum(items.qty) as ordered 
                    FROM `main` txn 
                    UNNEST txn.item_list AS items  
                    where txn.jsonType="Transaction" 
                    STR_TO_MILLIS(SUBSTR(txn.purchase_date, 0, LENGTH(txn.purchase_date)-3)) between STR_TO_MILLIS('{}') and STR_TO_MILLIS('{}')
                    group by items.sku, items.name_title, items.sale_price;'''.format(startDate, endDate)
        query = instance.main.n1ql_query(query)
        results = []
        for row in query:
            results.append(x)
        finalReturn = {}
        finalReturn['iTotalRecords'] = len(results)
        finalReturn['iTotalDisplayRecords'] = len(results)
        finalReturn['aaData'] = results
        return  finalReturn
    except Exception as e:
        print(e)
        finalReturn = {}
        finalReturn['iTotalRecords'] = 0
        finalReturn['iTotalDisplayRecords'] = 0
        finalReturn['aaData'] = {}
        return(finalReturn)
    
def save_cc(cbDoc, request):
#    print(request)
#    try:
        instance = get_couchbase()
        query = '''update `main` 
                    use keys "{}" 
                    set creditCards = ARRAY card for card in creditCards when card.name != "{}" end;'''.format(cbDoc, request['name'])
        instance.main.n1ql_query(query).execute()
        document = {}
        if str(request['cardNumber'])[0] == '4':
            request['name'] = "Visa_{}".format(str(request['cardNumber'])[-4:])
        elif str(request['cardNumber'])[0] == '5':
            request['name'] = "Mastercard_{}".format(str(request['cardNumber'])[-4:])
        else:
            request['name'] = "Error"
        document['active'] = str2bool(request['active'])
        document['ccNum'] = request['cardNumber']
        document['cid'] = request['cid']
        document['name'] = request['name']
        document['date'] = gt(request['exp']).isoformat()
        query = '''UPDATE `main` use keys '{}' set creditCards = ARRAY_APPEND(creditCards, {});'''.format(cbDoc, json.dumps(document))
        instance.main.n1ql_query(query).execute()
        return True
#    except Exception as e:
#        print(e)
#        return False

#demonstrate array append functionality
def add_cc(cbDoc, request):
    try:
        instance = get_couchbase()
        document = {}
        if str(request['cardNumber'])[0] == '4':
            request['name'] = "Visa_{}".format(str(request['cardNumber'])[-4:])
        elif str(request['cardNumber'])[0] == '5':
            request['name'] = "Mastercard_{}".format(str(request['cardNumber'])[-4:])
        else:
            request['name'] = "Error"
        document['active'] = str2bool(request['active'])
        document['ccNum'] = request['cardNumber']
        document['cid'] = request['cid']
        document['name'] = request['name']
        document['date'] = datetime.datetime(int(request['exp'].split("-")[0]), int(request['exp'].split("-")[1]), int(request['exp'].split("-")[2])).isoformat()
        query = '''UPDATE `main` use keys '{}' set creditCards = ARRAY_APPEND(creditCards, {});'''.format(cbDoc, json.dumps(document))
        instance.main.n1ql_query(query).execute()
        return True
    except Exception as e:
        print(e)
        return False

def delete_cc(cbDoc, request):
    try:
        instance = get_couchbase()
        query = '''update `main` 
                    use keys "{}" 
                    set creditCards = ARRAY card for card in creditCards when card.name != "{}" end;'''.format(cbDoc, request['name'])
        instance.main.n1ql_query(query).execute()
        return True
    except Exception as e:
        print(e)
        return False

def add_address(cbDoc, request):
    try:
        instance = get_couchbase()
        print(cbDoc)
        print(request)
        document = {}
        document['active'] = str2bool(request['active'])
        document['city'] = request['city']
        document['name'] = request['street1']
        document['state'] = request['state']
        document['street1'] = request['street1']
        document['street2'] = request['street2']
        document['zipcode'] = request['zip']
        query = '''UPDATE `main` use keys '{}' set shipping_address = ARRAY_APPEND(shipping_address, {});'''.format(cbDoc, json.dumps(document))
        instance.main.n1ql_query(query).execute()
        return True
    except Exception as e:
        print(e)
        print(query)
        return False

def save_address(cbDoc, request):
    try:
        instance = get_couchbase()
        query = '''update `main` 
                    use keys "{}" 
                    set shipping_address = ARRAY address for address in shipping_address when address.name != "{}" end;'''.format(cbDoc, request['name'])
        instance.main.n1ql_query(query).execute()
        document = {}
        document['active'] = str2bool(request['active'])
        document['city'] = request['city']
        document['name'] = request['street1']
        document['state'] = request['state']
        document['street1'] = request['street1']
        document['street2'] = request['street2']
        document['zipcode'] = request['zip']
        query = '''UPDATE `main` use keys '{}' set shipping_address = ARRAY_APPEND(shipping_address, {});'''.format(cbDoc, json.dumps(document))
        instance.main.n1ql_query(query).execute()
        return True
    except Exception as e:
        print(e)
        print(query)
        return False
    return True

def delete_address(cbDoc, request):
    try:
        instance = get_couchbase()
        query = '''update `main` 
                    use keys "{}" 
                    set shipping_address = ARRAY address for address in shipping_address when address.name != "{}" end;'''.format(cbDoc, request['name'])
        instance.main.n1ql_query(query).execute()
        return True
    except Exception as e:
        print(e)
        return False

###############################################################
#################Analytics queries#############################
###############################################################
#This section uses the analytics service. Faster performance due to 
#preaggregation. I think this could also be done with map/reduce views. Although 
#that would be inconsiderate of resources. 

#Gets the shopping cart totals. comparable to get_cart_total()
def getShoppingCartTotals():
    try:
        instance = get_couchbase()
        query = "select sum(extended_cost) as total_cost from `shoppingCarts` limit 1;"
        aQuery = AnalyticsQuery(query)
        result = instance.main.analytics_query(aQuery, '{}:8091'.format(instance.url))
        results = []
        for x in result:
            results.append(x)
        return results[0]
    except Exception as e:
        print(e)
        return({})

#Gets the total from transactions based on a time period. comparable to get_txn_total()
def getClosedSalesTotals(startDate, endDate):
    try:
        instance = get_couchbase()
        query = '''select sum(extended_cost) as total_cost from `transactions` 
                    where STR_TO_MILLIS(SUBSTR(purchase_date, 0, LENGTH(purchase_date)-3)) between STR_TO_MILLIS('{}') 
                    and STR_TO_MILLIS('{}');'''.format(startDate, endDate)
        print(query)
        aQuery = AnalyticsQuery(query)
        result = instance.main.analytics_query(aQuery, '{}:8091'.format(instance.url))
        results = []
        for x in result:
            results.append(x)
        return results[0]
    except Exception as e:
        print(e)
        return({})

#Gets all of the transactions for a time period and presents in a table format.
def getClosedItems(startDate, endDate):
    try:
        instance = get_couchbase()
        query = '''SELECT items.sku, items.sale_price, items.name_title, items.sum(items.qty) as ordered 
                    FROM `transactions` txn 
                    UNNEST txn.item_list AS items  
                    where STR_TO_MILLIS(SUBSTR(txn.purchase_date, 0, LENGTH(txn.purchase_date)-3)) between STR_TO_MILLIS('{}') and STR_TO_MILLIS('{}')
                    group by items.sku, items.name_title, items.sale_price;'''.format(startDate, endDate)
        aQuery = AnalyticsQuery(query)
        result = instance.main.analytics_query(aQuery, '{}:8091'.format(instance.url))
        results = []
        for x in result:
            results.append(x)
        finalReturn = {}
        finalReturn['iTotalRecords'] = len(results)
        finalReturn['iTotalDisplayRecords'] = len(results)
        finalReturn['aaData'] = results
        return finalReturn
    except Exception as e:
        print(e)
        finalReturn = {}
        finalReturn['iTotalRecords'] = 0
        finalReturn['iTotalDisplayRecords'] = 0
        finalReturn['aaData'] = {}
        return(finalReturn)



#Gets all of the shopping carts and puts the carts in a table format. 
def getCartItems():
    try:
        instance = get_couchbase()
        query = '''SELECT items.name_title, items.price, items.id, sum(items.qty) as ordered 
                    FROM `shoppingCarts` carts 
                    UNNEST carts.item_list AS items  
                    group by items.sku, items.id, items.price, items.name_title
                    order by sum(items.qty) desc
                    limit 50;'''
        aQuery = AnalyticsQuery(query)
        result = instance.main.analytics_query(aQuery, '{}:8091'.format(instance.url))
        results = []
        for x in result:
            results.append(x)
        finalReturn = {}
        finalReturn['iTotalRecords'] = len(results)
        finalReturn['iTotalDisplayRecords'] = len(results)
        finalReturn['aaData'] = results
        return  finalReturn
    except Exception as e:
        print(e)
        finalReturn = {}
        finalReturn['iTotalRecords'] = 0
        finalReturn['iTotalDisplayRecords'] = 0
        finalReturn['aaData'] = {}
        return(finalReturn)

if __name__ == "__main__":
    print(do_login("frederica_blunk@gmail.com", "Frederica"))
    print(get_products())
