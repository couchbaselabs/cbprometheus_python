from cb_utilities import *
import cb_cluster, cb_bucket
import sys
import json

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "xdcr"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},
                        {"variable":"buckets","type":"default","name":"bucket_list","value":[]},
                        {"variable":"result_set","type":"int","name":"num_samples","value":60}]
        self.comment = '''This is the method used to access xdcr metrics'''
        self.service_identifier = "kv"
        self.inputs = [{"value":"user"},
                        {"value":"passwrd"},
                        {"value":"cluster_values['serviceNodes']['{}']".format(self.service_identifier)},
                        {"value":"buckets"},
                        {"value":"cluster_values['clusterName']"},
                        {"value":"result_set"}]


def run(url="", user="", passwrd="", nodes=[], buckets=[], num_samples = 60, result_set=60):
    '''Entry point for getting the metrics for xdcr'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if num_samples != 60:
        result_set = num_samples
    try:
        if len(nodes) == 0:
            if len(buckets) == 0:
                if len(cluster_values['serviceNodes']['kv']) > 0:
                    bucket_metrics = cb_bucket._get_buckets(
                        cluster_values['serviceNodes']['kv'][0],
                        user,
                        passwrd)
            else:
                bucket_metrics = buckets
            xdcr_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['kv'],
                bucket_metrics, cluster_values['clusterName'],
                result_set)
            metrics = xdcr_metrics['metrics']

        else:
            if len(buckets) == 0:
                bucket_metrics = cb_bucket._get_metrics(
                    user, passwrd, nodes, cluster_values['clusterName'])
            else:
                bucket_metrics = {"buckets": buckets}

            xdcr_metrics = _get_metrics(
                user,
                passwrd,
                nodes,
                bucket_metrics['buckets'], cluster_values['clusterName'])

            metrics = xdcr_metrics['metrics']
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("Error getting xdcr started {}: {} {}, {}".format(nodes, str(e.args), exc_value, exc_traceback.tb_lineno))
    return metrics

def _get_metrics(user, passwrd, nodes, buckets, cluster_name="", result_set=60):
    '''XDCR metrics are gatherd here. First the links are queried, then it gathers
    the metrics for each link'''
    xdcr_metrics = {}
    xdcr_metrics['metrics'] = []
    auth = basic_authorization(user, passwrd)
    sample_list = get_sample_list(result_set)
    uri = ""
    try:
        for _uri in nodes:
            try:
                cluster_definition = {}
                _remote_cluster_url = "http://{}:8091/pools/default/" \
                                      "remoteClusters".format(_uri.split(":")[0])
                _rc_json = rest_request(auth, _remote_cluster_url)
                uri = _uri
                break
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print("Error getting xdcr node {}: {} {}, {}".format(uri, str(e.args), exc_value, exc_traceback.tb_lineno))
        for entry in _rc_json:
            cluster_definition[entry['uuid']] = {}
            cluster_definition[entry['uuid']]['hostname'] = entry['hostname']
            cluster_definition[entry['uuid']]['name'] = entry['name']

        try:
            _xdcr_url = "http://{}:8091/pools/default/tasks".format(uri.split(":")[0])
            _x_json = rest_request(auth, _xdcr_url)
            # get generic stats for each replication
            for record in _x_json:
                if record['type'] == "xdcr":
                    source = record['source']
                    dest_bucket = record['target'].split("/")[4]
                    remote_cluster_id = record['id'].split("/")[0]
                    replication_id = record['id']
                    hostname = cluster_definition[remote_cluster_id]['hostname']
                    remote_cluster_name = cluster_definition[remote_cluster_id]['name']
                    for metric in record:
                        if metric in ["source",
                                      "target",
                                      "id",
                                      "filterExpression",
                                      "continuous",
                                      "settingsURI",
                                      "maxVBReps",
                                      "replicationType",
                                      "type",
                                      "cancelURI"]:
                            pass
                        elif metric in ["status",
                                        "pauseRequested",
                                        "errors"]:
                            if metric == "status":
                                if record['status'] == "running":
                                    status = 0
                                elif record['status'] == "paused":
                                    status = 1
                                else:
                                    status = 2
                                xdcr_metrics['metrics'].append(
                                    "{} {{cluster=\"{}\", remote_cluster_id=\"{}\", "
                                    "replication_id=\"{}\", "
                                    "replication=\"{}\", "
                                    "level=\"cluster\", "
                                    "source_bucket=\"{}\", "
                                    "dest_cluster_name=\"{}\", "
                                    "dest_cluster_address=\"{}\", "
                                    "dest_bucket=\"{}\", "
                                    "type=\"xdcr\"}} {}".format(
                                        "status",
                                        cluster_name,
                                        remote_cluster_id,
                                        replication_id,
                                        "{} -> {} ({})".format(source, remote_cluster_name, dest_bucket),
                                        source,
                                        remote_cluster_name,
                                        hostname,
                                        dest_bucket,
                                        status))
                            elif metric == "pauseRequested":
                                if record['pauseRequested']:
                                    pause_requested = 1
                                else:
                                    pause_requested = 2
                                xdcr_metrics['metrics'].append(
                                    "{} {{cluster=\"{}\", remote_cluster_id=\"{}\", "
                                    "replication_id=\"{}\", "
                                    "replication=\"{}\", "
                                    "level=\"cluster\", "
                                    "source_bucket=\"{}\", "
                                    "dest_cluster_name=\"{}\", "
                                    "dest_cluster_address=\"{}\", "
                                    "dest_bucket=\"{}\", "
                                    "type=\"xdcr\"}} {}".format(
                                        "pause_requested",
                                        cluster_name,
                                        remote_cluster_id,
                                        replication_id,
                                        "{} -> {} ({})".format(source, remote_cluster_name, dest_bucket),
                                        source,
                                        remote_cluster_name,
                                        hostname,
                                        dest_bucket,
                                        pause_requested))
                            elif metric == "errors":
                                xdcr_metrics['metrics'].append(
                                    "{} {{cluster=\"{}\", remote_cluster_id=\"{}\", "
                                    "replication_id=\"{}\", "
                                    "replication=\"{}\", "
                                    "level=\"cluster\", "
                                    "source_bucket=\"{}\", "
                                    "dest_cluster_name=\"{}\", "
                                    "dest_cluster_address=\"{}\", "
                                    "dest_bucket=\"{}\", "
                                    "type=\"xdcr\"}} {}".format(
                                        "errors",
                                        cluster_name,
                                        remote_cluster_id,
                                        replication_id,
                                        "{} -> {} ({})".format(source, remote_cluster_name, dest_bucket),
                                        source,
                                        remote_cluster_name,
                                        hostname,
                                        dest_bucket,
                                        len(record[metric])))
                        elif metric in ['filterBypassExpiry', 'filterDeletion', 'filterExpiration']:
                            if record[metric] == True:
                                metric_value = 1
                            else:
                                metric_value = 0
                            xdcr_metrics['metrics'].append(
                                "{} {{cluster=\"{}\", remote_cluster_id=\"{}\", "
                                "replication_id=\"{}\", "
                                "replication=\"{}\", "
                                "level=\"cluster\", "
                                "source_bucket=\"{}\", "
                                "dest_cluster_name=\"{}\", "
                                "dest_cluster_address=\"{}\", "
                                "dest_bucket=\"{}\", "
                                "type=\"xdcr\"}} {}".format(
                                    snake_caseify(metric),
                                    cluster_name,
                                    remote_cluster_id,
                                    replication_id,
                                    "{} -> {} ({})".format(source, remote_cluster_name, dest_bucket),
                                    source,
                                    remote_cluster_name,
                                    hostname,
                                    dest_bucket,
                                    metric_value))
                        else:
                            xdcr_metrics['metrics'].append(
                                "{} {{cluster=\"{}\", remote_cluster_id=\"{}\", "
                                "replication_id=\"{}\", "
                                "replication=\"{}\", "
                                "level=\"cluster\", "
                                "source_bucket=\"{}\", "
                                "dest_cluster_name=\"{}\", "
                                "dest_cluster_address=\"{}\", "
                                "dest_bucket=\"{}\", "
                                "type=\"xdcr\"}} {}".format(
                                    snake_caseify(metric),
                                    cluster_name,
                                    remote_cluster_id,
                                    replication_id,
                                    "{} -> {} ({})".format(source, remote_cluster_name, dest_bucket),
                                    source,
                                    remote_cluster_name,
                                    hostname,
                                    dest_bucket,
                                    record[metric]))
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("xdcr in: {}: {}, {}".format(str(e.args), exc_value, exc_traceback.tb_lineno))
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("xcdr out: {}, {}, {}".format(str(e), exc_value, exc_traceback.tb_lineno))

    for node in nodes:
        for bucket in buckets:
            try:
                _node_url = "http://{}:8091/pools/default/buckets/" \
                            "@xdcr-{}/nodes/{}:8091/stats".format(node.split(":")[0],
                                                                  bucket,
                                                                  node.split(":")[0])
                n_json = rest_request(auth, _node_url)
                for entry in n_json['op']['samples']:
                    key_split = entry.split("/")
                    if "timestamp" not in key_split:
                        if len(key_split) == 5:
                            if key_split[4] != "":
                                if isinstance(n_json['op']['samples'][entry], type([])):
                                    for idx, datapoint in enumerate(n_json['op']['samples'][entry]):
                                        if idx in sample_list:
                                            xdcr_metrics['metrics'].append(
                                                "{} {{cluster=\"{}\", remote_cluster_id=\"{}\", "
                                                "replication_id=\"{}\", "
                                                "replication=\"{}\", "
                                                "level=\"node\", "
                                                "source_bucket=\"{}\", "
                                                "dest_cluster_name=\"{}\", "
                                                "dest_cluster_address=\"{}\", "
                                                "dest_bucket=\"{}\", "
                                                "type=\"xdcr\", "
                                                "node=\"{}\"}} {} {}".format(
                                                    snake_caseify(key_split[4]),
                                                    cluster_name,
                                                    key_split[1],
                                                    key_split[1] + "/" + key_split[2] + "/" + key_split[3],
                                                    key_split[2] + " -> " + cluster_definition[key_split[1]]['name'] + " (" + key_split[3] + ")",
                                                    key_split[2],
                                                    cluster_definition[key_split[1]]['name'],
                                                    cluster_definition[key_split[1]]['hostname'],
                                                    key_split[3],
                                                    node,
                                                    datapoint,
                                                    n_json['op']['samples']['timestamp'][idx]))
                        elif len(key_split) == 1:
                            for idx, datapoint in enumerate(
                                    n_json['op']['samples'][entry]):
                                xdcr_metrics['metrics'].append(
                                    "{} {{cluster=\"{}\", level=\"bucket\", "
                                    "bucket=\"{}\", "
                                    "type=\"xdcr\", "
                                    "node=\"{}\"}} {} {}".format(
                                        entry,
                                        cluster_name,
                                        bucket,
                                        node,
                                        datapoint,
                                        n_json['op']['samples']['timestamp'][idx]))
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print("xdcr: {}: {} {} {} {}".format(str(e), exc_value, exc_traceback.tb_lineno, node, bucket))
    return xdcr_metrics
