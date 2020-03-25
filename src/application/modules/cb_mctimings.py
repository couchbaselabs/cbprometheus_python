import re
import json
import subprocess
import timing_matrix
from cb_utilities import *
from datetime import datetime
import cb_cluster
import os

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "mctimings"
        self.filters = [{"variable":"buckets","type":"default","name":"bucket_list","value":[]},
                        {"variable":"nodes","type":"default","name":"nodes_list","value":[]}]
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

def process_metric_65(cmd, _range, value, cluster, node, bucket, _type="metric"):
    metric = []
    if _type == "metric":
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "le=\"{}\""
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            _range,
                            value))
    if _type == "count":
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\" "
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            value))

    return(metric[0])

def process_metric_pre65(cmd, _type, position, value, cluster, node, bucket, tm):

    if _type == "ms":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "le=\"{}\""
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
            "le=\"{}\""
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
            "le=\"{}\""
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            tm._500ms[str(position)],
                            value))
        return(metric[0])
    elif _type == "ns":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "le=\"{}\""
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            tm.ns,
                            value))
        return(metric[0])
    elif _type == "5s-9s":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "le=\"{}\""
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            tm._5s_9s,
                            value))
        return(metric[0])
    elif _type == "10s-19s":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "le=\"{}\""
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            tm._10s_19s,
                            value))
        return(metric[0])
    elif _type == "20s-39s":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "le=\"{}\""
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            tm._20s_39s,
                            value))
        return(metric[0])
    elif _type == "40s-79s":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "le=\"{}\""
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            tm._40s_79s,
                            value))
        return(metric[0])
    elif _type == "80s-inf":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "le=\"{}\""
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            tm._80s_inf,
                            value))
        return(metric[0])
    elif _type in ["command", "wayout"]:
        pass
    elif _type == "count":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
                            value))
        return(metric[0])
    elif _type == "sum":
        metric = []
        metric.append(
            "{} {{cluster=\"{}\", "
            "node=\"{}\", "
            "bucket=\"{}\", "
            "type=\"mctimings\", "
            "}} {}".format(cmd,
                            cluster,
                            node,
                            bucket,
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
            tm = timing_matrix.timing_matrix()
            for bucket in buckets:
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
                if len(stderr) > 0:
                    print("Error: {}".format(stderr))
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
                    count = 0
                    sum = 0
                    if mctiming['ns'] > 0:
                        mctiming_info['metrics'].append(
                            process_metric_pre65(
                                "{}_bucket".format(mctiming['command']),
                                "ns",
                                0,
                                mctiming['ns'],
                                cluster,
                                node,
                                bucket,
                                tm))
                        count += mctiming['ns']
                        sum = sum + (mctiming['ns'] * float(tm.ns))
                    for x, timing in enumerate(mctiming["us"]):
                        if timing > 0:
                            mctiming_info['metrics'].append(
                                process_metric_pre65(
                                    "{}_bucket".format(mctiming['command']),
                                    "us",
                                    x,
                                    timing + count,
                                    cluster,
                                    node,
                                    bucket,
                                    tm))
                            count += timing
                            sum = sum + (timing * float(tm.us[str(x)]))
                    for x, timing in enumerate(mctiming["ms"]):
                        if timing > 0:
                            mctiming_info['metrics'].append(
                                process_metric_pre65(
                                    "{}_bucket".format(mctiming['command']),
                                    "ms",
                                    x,
                                    timing + count,
                                    cluster,
                                    node,
                                    bucket,
                                    tm))
                            count += timing
                            sum = sum + (timing * float(tm.ms[str(x)]))
                    for x, timing in enumerate(mctiming["500ms"]):
                        if timing > 0:
                            mctiming_info['metrics'].append(
                                process_metric_pre65(
                                    "{}_bucket".format(mctiming['command']),
                                    "500ms",
                                    x,
                                    timing + count,
                                    cluster,
                                    node,
                                    bucket,
                                    tm))
                            count += timing
                            sum = sum + (timing * float(tm._500ms[str(x)]))
                    if mctiming['5s-9s'] > 0:
                        mctiming_info['metrics'].append(
                            process_metric_pre65(
                                "{}_bucket".format(mctiming['command']),
                                "5s-9s",
                                0,
                                count + mctiming['5s-9s'],
                                cluster,
                                node,
                                bucket,
                                tm))
                        count += mctiming['5s-9s']
                    if mctiming['10s-19s'] > 0:
                        mctiming_info['metrics'].append(
                            process_metric_pre65(
                                "{}_bucket".format(mctiming['command']),
                                "10s-19s",
                                0,
                                count + mctiming['10s-19s'],
                                cluster,
                                node,
                                bucket,
                                tm))
                        count += mctiming['10s-19s']
                        sum = sum + (timing * float(tm['10s-19s']))
                    if mctiming['20s-39s'] > 0:
                        mctiming_info['metrics'].append(
                            process_metric_pre65(
                                "{}_bucket".format(mctiming['command']),
                                "20s-39s",
                                0,
                                mctiming['20s-39s'],
                                cluster,
                                node,
                                bucket,
                                tm))
                        count += mctiming['20s-39s']
                        sum = sum + (timing * float(tm['20s-39s']))
                    if mctiming['20s-39s'] > 0:
                        mctiming_info['metrics'].append(
                            process_metric_pre65(
                                "{}_bucket".format(mctiming['command']),
                                "40s-79s",
                                0,
                                count + mctiming['40s-79s'],
                                cluster,
                                node,
                                bucket,
                                tm))
                        count += mctiming['40s-79s']
                        sum = sum + (timing * float(tm._40s_79s))
                    if count + mctiming['80s-inf'] > 0:
                        mctiming_info['metrics'].append(
                            process_metric_pre65(
                                "{}_bucket".format(mctiming['command']),
                                "80s-inf",
                                0,
                                count + mctiming['80s-inf'],
                                cluster,
                                node,
                                bucket,
                                tm))
                        count += mctiming['80s-inf']
                        sum = sum + (timing * float(tm._40s_79s))
                    if count > 0:
                        mctiming_info['metrics'].append(
                            process_metric_pre65(
                                "{}_count".format(mctiming['command']),
                                "count",
                                0,
                                count,
                                cluster,
                                node,
                                bucket,
                                tm))
                        mctiming_info['metrics'].append(
                            process_metric_pre65(
                                "{}_sum".format(mctiming['command']),
                                "sum",
                                0,
                                sum,
                                cluster,
                                node,
                                bucket,
                                tm))
        else:
            for bucket in buckets:
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
                if len(stderr) > 0:
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
                    count = 0
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
                                        {"{}".format(count + entry[0]): entry[1]}))
                                lowPos = entry[0]
                                count += entry[0]
                        inner_metric.append({"+Inf".format(lowPos): 0})
                    for _metric in inner_metric:
                        for i in _metric:
                            mctiming_info['metrics'].append(
                                process_metric_65(
                                    "{}_bucket".format(metric['command']),
                                    i,
                                    _metric[i]+ count,
                                    cluster,
                                    node,
                                    bucket))
                            count += _metric[i]
                    if count > 0:
                        mctiming_info['metrics'].append(
                            process_metric_65(
                                "{}_count".format(metric['command']),
                                i,
                                count,
                                cluster,
                                node,
                                bucket,
                                "count"))
    return(mctiming_info)


if __name__ == "__main__":
    start_t = datetime.now()
    #print(_get_metrics("Administrator", "password", "TestCluster", ['travel-sample'], ["18.224.34.238"]))
    for entry in run("18.224.34.238", "Administrator", "password", ["travel-sample"], ["18.224.34.238"], ""):
        print(entry)
    #print(get_version("18.224.34.238", "Administrator", "password"))
    print(datetime.now() - start_t)
