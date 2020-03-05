import re
import json
import subprocess
import timing_matrix
from cb_utilities import *
from datetime import datetime
import cb_cluster

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "mctimings"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},
                        {"variable":"buckets","type":"default","name":"bucket_list","value":[]}]
        self.comment = '''This is the method used to access mctiming'''
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
    '''Entry point for getting the mctimings'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    print(cluster_values['serviceNodes']['kv'])
    node_list = []
    if len(buckets) == 0:
        buckets = get_buckets(url, user, passwrd)
    for _node in cluster_values['serviceNodes']['kv']:
        node_list.append(_node.split(":")[0])
    if cluster == "":
        cluster = cluster_values['clusterName']
    if len(nodes) == 0:
        if len(cluster_values['serviceNodes']['kv']) > 0:
            mctiming_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['clusterName'],
                buckets,
                node_list)
            metrics = filter(None, mctiming_metrics['metrics'])
    else:
        mctiming_metrics = _get_metrics(
            user, passwrd, cluster_values['clusterName'], buckets, nodes)
        metrics = filter(None, mctiming_metrics['metrics'])
    return metrics

def process_metric_65(cmd, _range, value, cluster, node, bucket):
    metric = []
    metric.append(
        "{} {{cluster=\"{}\", "
        "node=\"{}\", "
        "bucket=\"{}\", "
        "type=\"mctimings\", "
        "range=\"{}\""
        "}} {}".format(cmd,
                        cluster,
                        node,
                        bucket,
                        _range,
                        value))
    return(metric[0])

def process_metric_pre65(cmd, _type, position, value, cluster, node, bucket):
    tm = timing_matrix.timing_matrix()
    if _type == "ms":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "range=\"{}\""
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            tm.ms[str(position)],
                            value))
        return(metric[0])
    elif _type == "us":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "range=\"{}\""
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            tm.us[str(position)],
                            value))
        return(metric[0])
    elif _type == "500ms":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "range=\"{}\""
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            tm._500ms[str(position)],
                            value))
        return(metric[0])
    elif _type in ["command", "ns", "wayout"]:
        pass
    else:
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "range=\"{}\", "
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            _type,
                            value))
        return(metric[0])

def get_version(url="", user="", passwrd=""):
    _url = "http://{}:8091/pools".format(url)
    auth = basic_authorization(user, passwrd)
    f_json = rest_request(auth, _url)
    version = float("{}.{}".format(f_json['implementationVersion'].split(".")[0], f_json['implementationVersion'].split(".")[1]))
    return(version)

def _get_metrics(user="", passwrd="", cluster="", buckets=[], nodes = []):
    mctiming_info = {}
    mctiming_info['buckets'] = []
    mctiming_info['metrics'] = []

    for node in nodes:
        version = get_version(node, user, passwrd)

        if version < 6.5:
            for bucket in buckets:
                import os

                dirpath = os.getcwd()
                _path = dirpath.split("/")
                backup = "../" * (_path[::-1].index("src")+0)
                proc = subprocess.Popen(['{}application/resources/mctimings'.format(backup),
                                        '-h', '{}:11210'.format(node),
                                        '-u', user,
                                        '-P', passwrd,
                                        '-b', bucket,
                                        '-j'], stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE,
                                               stdin=subprocess.PIPE)

                stdout, stderr = proc.communicate()
                if stderr != None:
                    print(stderr)
                new_stdout = re.sub('\s+', " ", stdout)
                arr_stdout = new_stdout.split("} {")
                arr_mctimings = []
                for x in arr_stdout:
                    new_str = x.strip()
                    if new_str[0:1] != "{":
                        new_str = "{" + new_str
                    if new_str[-1:] != "}":
                        new_str = new_str + "}"
                    arr_mctimings.append(json.loads(new_str))
                for mctiming in arr_mctimings:
                    for key in mctiming:
                        if type(mctiming[key]) == type([]):
                            for x, timing in enumerate(mctiming[key]):
                                mctiming_info['metrics'].append(
                                    process_metric_pre65(
                                        mctiming['command'],
                                        key,
                                        x,
                                        timing,
                                        cluster,
                                        node,
                                        bucket))
                        else:
                            mctiming_info['metrics'].append(
                                process_metric_pre65(
                                    mctiming['command'],
                                    key,
                                    0,
                                    mctiming[key],
                                    cluster,
                                    node,
                                    bucket))
        else:
            for bucket in buckets:
                import os

                dirpath = os.getcwd()
                _path = dirpath.split("/")
                backup = "../" * (_path[::-1].index("src")+0)
                proc = subprocess.Popen(['{}application/resources/mctimings'.format(backup),
                                        '-h', '{}:11210'.format(node),
                                        '-u', user,
                                        '-P', passwrd,
                                        '-b', bucket,
                                        '-j'], stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE,
                                               stdin=subprocess.PIPE)

                stdout, stderr = proc.communicate()
                if stderr != None:
                    print(stderr)
                new_stdout = re.sub('\s+', " ", stdout)
                arr_stdout = new_stdout.split("} {")
                arr_mctimings = []
                for x in arr_stdout:
                    new_str = x.strip()
                    if new_str[0:1] != "{":
                        new_str = "{" + new_str
                    if new_str[-1:] != "}":
                        new_str = new_str + "}"
                    arr_mctimings.append(json.loads(new_str))
                for metric in arr_mctimings:
                    lowPos = metric['bucketsLow']
                    inner_metric = []
                    if metric['total'] == 0:
                        pass
                    else:
                        for entry in metric['data']:
                            if entry[0] == lowPos:
                                pass
                            else:
                                mctiming_info['metrics'].append(
                                    inner_metric.append(
                                        {"{}-{}ms".format(lowPos,
                                        entry[0]): entry[1]}))
                                lowPos = entry[0]
                        inner_metric.append({"{}-inf".format(lowPos): 0})
                    for _metric in inner_metric:
                        for i in _metric:
                            mctiming_info['metrics'].append(
                                process_metric_65(
                                    metric['command'],
                                    i,
                                    _metric[i],
                                    cluster,
                                    node,
                                    bucket))
            return(mctiming_info)


if __name__ == "__main__":
    start_t = datetime.now()
    #print(_get_metrics("Administrator", "password", "TestCluster", ['travel-sample'], ["18.224.34.238"]))
    for entry in run("18.224.34.238", "Administrator", "password", ["test"], [], ""):
        print(entry)
    #print(get_version("18.224.34.238", "Administrator", "password"))
    print(datetime.now() - start_t)
