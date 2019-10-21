from cb_utilities import *

def _get_xdcr_metrics(user, passwrd, nodes, buckets, cluster_name=""):
    '''XDCR metrics are gatherd here. First the links are queried, then it gathers
    the metrics for each link'''
    xdcr_metrics = {}
    xdcr_metrics['metrics'] = []

    auth = basic_authorization(user, passwrd)

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
                print("Error getting xdcr node {}: {}".format(uri, str(e.args)))
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
                    _id = record['id'].split("/")[0]
                    hostname = value_to_string(cluster_definition[_id]['hostname'])
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
                                    "{} {{cluster=\"{}\", instanceID=\"{}\", "
                                    "level=\"cluster\", "
                                    "sourceBucket=\"{}\", "
                                    "destClusterName=\"{}\", "
                                    "destClusterAddress=\"{}\", "
                                    "destBucket=\"{}\", "
                                    "type=\"xdcr\"}} {}".format(
                                        "status",
                                        cluster_name,
                                        _id,
                                        source,
                                        cluster_definition[_id]['name'],
                                        hostname,
                                        dest_bucket,
                                        status))
                            elif metric == "pauseRequested":
                                if record['pauseRequested']:
                                    pause_requested = 1
                                else:
                                    pause_requested = 2
                                xdcr_metrics['metrics'].append(
                                    "{} {{cluster=\"{}\", instanceID=\"{}\", "
                                    "level=\"cluster\", "
                                    "sourceBucket=\"{}\", "
                                    "destClusterName=\"{}\", "
                                    "destClusterAddress=\"{}\", "
                                    "destBucket=\"{}\", "
                                    "type=\"xdcr\"}} {}".format(
                                        "pauseRequested",
                                        cluster_name,
                                        _id,
                                        source,
                                        cluster_definition[_id]['name'],
                                        hostname,
                                        dest_bucket,
                                        pause_requested))
                            elif metric == "errors":
                                xdcr_metrics['metrics'].append(
                                    "{} {{cluster=\"{}\", instanceID=\"{}\", "
                                    "level=\"cluster\", "
                                    "sourceBucket=\"{}\", "
                                    "destClusterName=\"{}\", "
                                    "destClusterAddress=\"{}\", "
                                    "destBucket=\"{}\", "
                                    "type=\"xdcr\"}} {}".format(
                                        "errors",
                                        cluster_name,
                                        _id,
                                        source,
                                        cluster_definition[_id]['name'],
                                        hostname,
                                        dest_bucket,
                                        len(record[metric])))
                        else:
                            xdcr_metrics['metrics'].append(
                                "{} {{cluster=\"{}\", instanceID=\"{}\", "
                                "level=\"cluster\", "
                                "sourceBucket=\"{}\", "
                                "destClusterName=\"{}\", "
                                "destClusterAddress=\"{}\", "
                                "destBucket=\"{}\", "
                                "type=\"xdcr\"}} {}".format(
                                    metric,
                                    cluster_name,
                                    _id,
                                    source,
                                    cluster_definition[_id]['name'],
                                    hostname,
                                    dest_bucket,
                                    record[metric]))
        except Exception as e:
            print("xdcr in: " + str(e))
    except Exception as e:
        print("xcdr out: " + str(e))

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
                                        xdcr_metrics['metrics'].append(
                                            "{} {{cluster=\"{}\", instanceID=\"{}\", "
                                            "level=\"node\", "
                                            "sourceBucket=\"{}\", "
                                            "destClusterName=\"{}\", "
                                            "destClusterAddress=\"{}\", "
                                            "destBucket=\"{}\", "
                                            "type=\"xdcr\", "
                                            "node=\"{}\"}} {} {}".format(
                                                key_split[4],
                                                cluster_name,
                                                key_split[1],
                                                key_split[2],
                                                value_to_string(
                                                    cluster_definition[key_split[1]]['name']),
                                                value_to_string(
                                                    cluster_definition[key_split[1]]['hostname']),
                                                key_split[3], value_to_string(node),
                                                datapoint,
                                                n_json['op']['samples']['timestamp'][idx]))
                        elif len(key_split) == 1:
                            for idx, datapoint in enumerate(
                                    n_json['op']['samples'][entry]):
                                xdcr_metrics['metrics'].append(
                                    "{} {{cluster=\"{}\", level=\"bucket\", "
                                    "source=\"{}\", "
                                    "type=\"xdcr\", "
                                    "node=\"{}\"}} {} {}".format(
                                        entry,
                                        cluster_name,
                                        bucket,
                                        value_to_string(node),
                                        datapoint,
                                        n_json['op']['samples']['timestamp'][idx]))
            except Exception as e:
                print("xdcr: " + str(e))
    return xdcr_metrics
