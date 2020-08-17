import json
import re
from random import shuffle
from datetime import datetime
import socket
import sys


if sys.version_info[0] == 3:
    from urllib.request import *
    import base64
else:
    from urllib2 import *

class Error(Exception):
   """Base class for other exceptions"""
   pass

class SeedNodeDown(Error):
   """Raised when all the seed nodes are down"""
   pass

def get_sample_list(num_results):
    y = 60/int(num_results)
    int_arry = []
    for x in range(0,60):
        if (x) % y == 0:
            int_arry.append(59-x)
    return(int_arry)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return [IP]

def get_dt():
    epoch = datetime.utcfromtimestamp(0)
    return '%.0f' % ((datetime.now() - epoch).total_seconds() * 1000)

def snake_caseify(input_str):
    '''converts to snake case'''
    converted_str = '_'.join(filter(None, re.split("([A-Z][^A-Z]*)", input_str))).lower()
    return converted_str

def basic_authorization(user, password):
    '''Doc String'''
    s = user + ":" + password
    if sys.version_info[0] == 3:
        return_string = "Basic " + base64.b64encode(bytes(s, 'utf-8')).decode('ascii')
        return return_string
    else:
        return_string = "Basic " + s.encode("base64").rstrip()
        return return_string

def str2bool(v):
    '''Converts string values to boolean'''
    return v.lower() in ("yes", "true", "t", "1")

def value_to_string(ip_address):
    '''converts values to strings without special characters'''
    ip_address = ip_address.split(":")[0].replace(".", "_").replace("+", "_").replace("+", "_")
    return ip_address

def rest_request(auth, url):
    _url = url
    req = Request(_url,
                          headers={
                              "Authorization": auth,
                              "Content-Type": "application/x-www-form-urlencoded",

                              # Some extra headers for fun
                              "Accept": "*/*",  # curl does this
                              "User-Agent": "check_version/1",
                          })

    f = (urlopen(req, timeout=1)).read()
    result = json.loads(f)
    return result

def text_request(url):
    _url = url
    req = Request(_url,
                          headers={
                              "Content-Type": "application/x-www-form-urlencoded",

                              # Some extra headers for fun
                              "Accept": "*/*",  # curl does this
                              "User-Agent": "check_version/1",
                          })
    f = (urlopen(req, timeout=0.1)).readlines()
    return(f)

def check_cluster(url, username, pw):
    urls = url.split(",")
    shuffle(urls)
    active = False
    auth = basic_authorization(username, pw)
    for _url in urls:
        try:
            rest_request(auth, "http://{}:8091/pools/default".format(_url))
            url = _url
            active = True
            break
        except Exception as e:
            print(e)
            pass
    if active == False:
        raise SeedNodeDown
    else:
        return url
