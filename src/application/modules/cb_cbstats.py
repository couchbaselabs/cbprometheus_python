import json
import subprocess
from datetime import datetime
import os
import sys

if sys.version_info[0] == 3:
    from .cb_utilities import *
    from . import cb_cluster, cb_bucket, timing_matrix
    from .remote_control import SSH_controller
else:
    from cb_utilities import *
    import cb_cluster, cb_bucket, timing_matrix
    from remote_control import SSH_controller

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "cbstats"
        self.filters = [{"variable":"buckets","type":"default","name":"bucket_list","value":[]},
                        {"variable":"nodes","type":"default","name":"nodes_list","value":[]},
                        {"variable":"key", "type":"configuration","name":"application.config['CB_KEY']", "value":""},
                        {"variable":"cb_stat_path", "type":"configuration","name":"application.config['CB_CBSTAT_PATH']", "value":""},
                        {"variable":"ssh_user", "type":"configuration","name":"application.config['CB_SSH_UN']", "value":""},
                        {"variable":"ssh_host", "type":"configuration","name":"application.config['CB_SSH_HOST']", "value":""}]
        self.comment = '''This is the method used to access cbstats'''
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

def run(url="", user="", passwrd="", buckets=[], nodes=[], key = "",
            cbstat_path = "", ssh_un = "", ssh_host = "", result_set=60):
    '''Entry point for getting the cbstats'''

    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    node_list = []
    if len(buckets) == 0:
        buckets = get_buckets(url, user, passwrd)
    for _node in cluster_values['serviceNodes']['kv']:
        node_list.append(_node.split(":")[0])
    cluster = cluster_values['clusterName']
    if len(nodes) == 0:
        if len(cluster_values['serviceNodes']['kv']) > 0:
            cbstats_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['clusterName'],
                buckets,
                node_list,
                ssh_un,
                key,
                cbstat_path,
                ssh_host)
            metrics = filter(None, cbstats_metrics['metrics'])
    else:
        cbstats_metrics = _get_metrics(user,
                                        passwrd,
                                        cluster_values['clusterName'],
                                        buckets,
                                        nodes,
                                        ssh_un,
                                        key,
                                        cbstat_path,
                                        ssh_host)
        metrics = filter(None, cbstats_metrics['metrics'])
    return metrics

def _get_metrics(user="", passwrd="", cluster="", buckets=[], nodes = [],
                    ssh_username="", key="", cbstat_path="",
                    ssh_host=""):
    cbstat_info = {}
    cbstat_info['buckets'] = []
    cbstat_info['metrics'] = []

    if cbstat_path is None:
        cbstat_path = "/opt/couchbase/bin/cbstats"
    ssh_controller = SSH_controller("cbstats", key, ssh_username, user, passwrd)


    for node in nodes:
        for bucket in buckets:
            try:
                result = ssh_controller.get_connection(node, bucket, cbstat_path, ssh_host)
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
            except Exception as e:
                print(e)
    return(cbstat_info)


if __name__ == "__main__":
    start_t = datetime.now()
    #print(_get_metrics("Administrator", "password", "TestCluster", ['travel-sample'], ["18.224.34.238"]))
    for entry in run("18.224.34.238", "Administrator", "password", ["travel-sample"], ["18.224.34.238"], ""):
        print(entry)
    #print(get_version("18.224.34.238", "Administrator", "password"))
    print(datetime.now() - start_t)
