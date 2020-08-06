import json
import subprocess
from datetime import datetime
import os
import sys

if sys.version_info[0] == 3:
    from .cb_utilities import *
    from . import cb_cluster, cb_bucket, timing_matrix
else:
    from cb_utilities import *
    import cb_cluster, cb_bucket, timing_matrix

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "cbstats"
        self.filters = [{"variable":"buckets","type":"default","name":"bucket_list","value":[]},
                        {"variable":"nodes","type":"default","name":"nodes_list","value":[]}]
        self.comment = '''This is the method used to access cbstat'''
        self.service_identifier = "kv"
        self.inputs = [{"value":"user"},
                        {"value":"passwrd"},
                        {"value":"bucket_list"},
                        {"value":"cluster_values['serviceNodes']['{}']".format(self.service_identifier)},
                        {"value":"cluster_values['clusterName']"}]
        self.exclude = True

def get_buckets(url, user, passwrd):
    auth = basic_authorization(user, passwrd)
    url = "http://{}:8091/pools/default/buckets".format(url.split(":")[0])
    f_json = rest_request(auth, url)
    buckets = []
    for bucket in f_json:
        buckets.append(bucket['name'])
    buckets.sort()
    return(buckets)

def run(url="", user="", passwrd="", buckets=[], nodes=[], cluster=""):
    '''Entry point for getting the cbstats'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    node_list = []
    if len(buckets) == 0:
        buckets = get_buckets(url, user, passwrd)
    for _node in cluster_values['serviceNodes']['kv']:
        node_list.append(_node.split(":")[0])
    if cluster == "":
        cluster = cluster_values['clusterName']
    if len(nodes) == 0:
        if len(cluster_values['serviceNodes']['kv']) > 0:
            cbstats_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['clusterName'],
                buckets,
                node_list)
            metrics = filter(None, cbstats_metrics['metrics'])
    else:
        cbstats_metrics = _get_metrics(
            user, passwrd, cluster_values['clusterName'], buckets, nodes)
        metrics = filter(None, cbstats_metrics['metrics'])
    return metrics

def _get_metrics(user="", passwrd="", cluster="", buckets=[], nodes = []):
    cbstat_info = {}
    cbstat_info['buckets'] = []
    cbstat_info['metrics'] = []

    # determine executable path to cbstats
    dirpath = os.getcwd()
    _path = dirpath.split("/")
    backup = "../" * (_path[::-1].index("src")+0)
    # default to cbstats with the project
    exec_path='{}application/resources/cbstats'.format(backup)
    # check to see if cbstats exists
    if (os.path.isfile("/opt/couchbase/bin/cbstats")):
        exec_path = '/opt/couchbase/bin/cbstats'
    elif (os.path.isfile('/Applications/Couchbase Server.app/Contents/Resources/couchbase-core/bin/cbstats')):
        exec_path = '/Applications/Couchbase Server.app/Contents/Resources/couchbase-core/bin/cbstats'
    for node in nodes:
        for bucket in buckets:
            proc = subprocess.Popen([exec_path,
                                    '{}:11210'.format(node),
                                    '-u', user,
                                    '-p', passwrd,
                                    '-b', bucket,
                                    '-j',
                                    'all'], stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           stdin=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            if len(stderr) > 0:
                print("Error: {}".format(stderr))
            result = json.loads(stdout)
            for record in result:
                # only output results that are a number
                if isinstance(result[record], (int, float)) == True:
                    cbstat_info['metrics'].append(
                        "{} {{cluster=\"{}\", node=\"{}\", bucket=\"{}\", "
                        "type=\"cbstats\"}} {}".format(
                            value_to_string(record),
                            cluster,
                            node,
                            bucket,
                            result[record]))
                elif str(result[record]).lower() == "true" or str(result[record]).lower() == "false":
                    cbstat_info['metrics'].append(
                        "{} {{cluster=\"{}\", node=\"{}\", bucket=\"{}\", "
                        "type=\"cbstats\"}} {}".format(
                            value_to_string(record),
                            cluster,
                            node,
                            bucket,
                            int(str2bool(str(result[record])))))
    return(cbstat_info)


if __name__ == "__main__":
    start_t = datetime.now()
    #print(_get_metrics("Administrator", "password", "TestCluster", ['travel-sample'], ["18.224.34.238"]))
    for entry in run("18.224.34.238", "Administrator", "password", ["travel-sample"], ["18.224.34.238"], ""):
        print(entry)
    #print(get_version("18.224.34.238", "Administrator", "password"))
    print(datetime.now() - start_t)
