__author__ = "tdenton"
__date__ = "$Apr 27, 2019$"

from couchbase.bucket import Bucket
from couchbase.n1ql import N1QLQuery
from couchbase.cluster import Cluster, ClassicAuthenticator, PasswordAuthenticator
import json
import urllib2

#Storing the address username and password in this file is the wrong way to do 
#things but it works for the demo 
DEFAULT_USER = "Administrator"
DEFAULT_PW = "password123"
DEFAULT_URL = "cbdata-1.querc.org"
#DEFAULT_URL = "192.168.1.3"


#This is used to connect to couchbase, get the version and connect using the 
#appropriate method for connection. The difference in connection is between 4 and 5
class cb_bucket():
    def __init__(self):
        self.get_buckets()
    def get_buckets(self):
        self.cdr = Bucket('{}/main'.format(self.url), password='')
        self.hxn = Bucket('{}/hxn'.format(self.url), password='')
            
class auth_cb_cluster():
    def __init__(self):
        self.default_user = DEFAULT_USER
        self.default_pw = DEFAULT_PW
        self.default_url = DEFAULT_URL
        self.get_authenticated()
    def get_authenticated(self):
        try:
            self.user = self.default_user
            self.passwrd = self.default_pw
            self.url = self.default_url
        except Exception as e:
            self.user = "Administrator"
            self.passwrd = "password123"
            self.url = "0.0.0.0"
        
        self.version = self.get_version()
        print(self.version)
        if self.version >= 5:
            self.cluster = Cluster('couchbase://{}'.format(self.url))         
            self.authenticator = PasswordAuthenticator(self.user, self.passwrd)
            self.cluster.authenticate(self.authenticator)
            self.main = self.cluster.open_bucket('main')
            self.hxn = self.cluster.open_bucket('hxn')
            self.main._cntlstr("operation_timeout", "5000")
        else:
            self.cluster = Cluster('couchbase://{}'.format(self.url)) 
            self.cluster.authenticate(ClassicAuthenticator(buckets={'main':'', 'hxn':''}))
            self.main = self.cluster.open_bucket('main')
            self.hxn = self.cluster.open_bucket('hxn')
            
    def basic_authorization(self, user, password):
        s = user + ":" + password
        return "Basic " + s.encode("base64").rstrip()

    def get_version(self):
        try:
            url = "http://{}:8091/pools".format(self.url)
            req = urllib2.Request(url,
                                  headers={
                                  "Authorization": self.basic_authorization(self.user, self.passwrd),
                                  "Content-Type": "application/x-www-form-urlencoded",

                                  # Some extra headers for fun
                                  "Accept": "*/*", # curl does this
                                  "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                                  })

            f = (urllib2.urlopen(req)).read()
            f_json = json.loads(f)
            version = float("{}.{}".format(f_json['implementationVersion'].split(".")[0], f_json['implementationVersion'].split(".")[1]))
            return(version)
        except Exception as e:
            print("Curl Error:", e.args)
            return(4.5)
            
def get_class_bucket(env):
    instance = cb_bucket(env)
    return instance

def get_bucket(env, bkt):
    print env, bkt.upper()
    if bkt.upper() == "MAIN":
        if env.upper() == "ERROR":
            cb = Bucket("couchbase://{}/main".format(DEFAULT_URL), password='')
    if bkt.upper() == "HXN":
        if env.upper() == "ERROR":
            cb = Bucket("couchbase://{}/hxn".format(DEFAULT_URL), password='')
    return cb

def get_cluster(env):
    instance = auth_cb_cluster()
    return instance
        