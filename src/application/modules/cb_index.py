import sys
from application import application
if sys.version_info[0] == 3:
    from .cb_utilities import *
    from . import cb_cluster, cb_bucket
else:
    from cb_utilities import *
    import cb_cluster, cb_bucket

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "indexes"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},
                        {"variable":"buckets","type":"default","name":"bucket_list","value":[]},
                        {"variable":"indexes","type":"default","name":"indexes_list","value":[]},
                        {"variable":"result_set","type":"int","name":"num_samples","value":60}]
        self.comment = '''This is the method used to access FTS metrics'''
        self.service_identifier = "index"
        self.inputs = [{"value":"user"},
                        {"value":"passwrd"},
                        {"value":"cluster_values['serviceNodes']['{}']".format(self.service_identifier)},
                        {"value": "index_buckets"},
                        {"value":"cluster_values['clusterName']"},
                        {"value":"result_set"}]
        self.exclude = False


def run(url="", user="", passwrd="", index=[], buckets=[], nodes=[], num_samples = 60, result_set=60):
    '''Entry point for getting the metrics for the index nodes'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if num_samples != 60:
        result_set = num_samples
    if len(buckets) == 0:
        buckets = cb_bucket._get_index_buckets(url, user, passwrd)

    # get the index replica stats
    index_replicas = _get_index_replica_counts(url, user, passwrd, cluster_values['clusterName'])
    metrics = metrics + index_replicas['metrics']

    if len(nodes) == 0:
        if len(cluster_values['serviceNodes']['index']) > 0 and len(buckets) > 0:
            index_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['index'],
                buckets,
                cluster_values['clusterName'],
                result_set)

            metrics = metrics + index_metrics['metrics']
    else:

        if len(buckets) > 0:
            index_metrics = _get_metrics(
                user,
                passwrd,
                nodes,
                buckets,
                cluster_values['clusterName'],
                result_set)

            metrics = metrics + index_metrics['metrics']

    return metrics

def _get_metrics(user, passwrd, nodes, buckets, cluster_name="", result_set=60):
    '''Gets the metrics for the indexes nodes, then gets the metrics for each index'''
    index_info = {}
    index_info['metrics'] = []
    auth = basic_authorization(user, passwrd)
    sample_list = get_sample_list(result_set)
    # get cluster index info
    for node in nodes:
        node_hostname = node.split(":")[0]
        _index_url = "http://{}:8091/pools/default/buckets/@index/nodes/{}:8091/stats".format(
            node_hostname, node_hostname)
        try:
            i_json = rest_request(auth, _index_url)
            samples_count = len(i_json['op']['samples'][record])
            for record in i_json['op']['samples']:
                if record != "timestamp":
                    # if the sample list value is greater than the samples count, just use the last sample
                    if samples_count < sample_list[0]:
                        index_info['metrics'].append(
                            "{} {{cluster=\"{}\", node=\"{}\", "
                            "type=\"index-service\"}} {} {}".format(
                                record,
                                cluster_name,
                                node_hostname,
                                i_json['op']['samples'][record][samples_count - 1],
                                i_json['op']['samples']['timestamp'][samples_count - 1]
                            )
                        )
                    else:
                        for idx, datapoint in enumerate(i_json['op']['samples'][record]):
                            if idx in sample_list:
                                index_info['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "type=\"index-service\"}} {} {}".format(
                                        record,
                                        cluster_name,
                                        node_hostname,
                                        datapoint,
                                        i_json['op']['samples']['timestamp'][idx]))

        except Exception as e:
            print("index base: " + str(e))

    for node in nodes:
        node_hostname = node.split(":")[0]
        for bucket in buckets:
            try:
                index_info_url = "http://{}:8091/pools/default/buckets/@index-{}/" \
                                 "nodes/{}:8091/stats".format(node_hostname,
                                                              bucket,
                                                              node_hostname)
                ii_json = rest_request(auth, index_info_url)
                for record in ii_json['op']['samples']:
                    name = ""
                    index_type = ""
                    try:
                        split_record = record.split("/")
                        samples_count = len(ii_json['op']['samples'][record])
                        if len(split_record) == 3:
                            name = (split_record[1]).replace("+", "_")
                            index_type = (split_record[2]).replace("+", "_")
                            if isinstance(ii_json['op']['samples'][record], type([])):
                                # if the sample list value is greater than the samples count, just use the last sample
                                if samples_count < sample_list[0]:
                                    index_info['metrics'].append(
                                        "{} {{cluster=\"{}\", node=\"{}\","
                                        "index=\"{}\", "
                                        "bucket=\"{}\", "
                                        "type=\"index\"}} {} {}".format(
                                            index_type,
                                            cluster_name,
                                            node_hostname,
                                            name,
                                            bucket,
                                            ii_json['op']['samples'][record][samples_count - 1],
                                            ii_json['op']['samples']['timestamp'][samples_count - 1]
                                        )
                                    )
                                else:
                                    for idx, datapoint in enumerate(ii_json['op']['samples'][record]):
                                        if idx in sample_list:
                                            index_info['metrics'].append(
                                                "{} {{cluster=\"{}\", node=\"{}\","
                                                "index=\"{}\", "
                                                "bucket=\"{}\", "
                                                "type=\"index\"}} {} {}".format(
                                                    index_type,
                                                    cluster_name,
                                                    node_hostname,
                                                    name,
                                                    bucket,
                                                    datapoint,
                                                    ii_json['op']['samples']['timestamp'][idx]
                                                )
                                            )
                            else:
                                index_info['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "index=\"{}\", "
                                    "bucket=\"{}\", "
                                    "type=\"index\"}} {}".format(
                                        index_type,
                                        cluster_name,
                                        node_hostname,
                                        name,
                                        bucket,
                                        ii_json['op']['samples'][record]
                                    )
                                )

                        elif len(split_record) == 2:
                            index_type = split_record[1]
                            if isinstance(ii_json['op']['samples'][record], type([])):
                                # if the sample list value is greater than the samples count, just use the last sample
                                if samples_count < sample_list[0]:
                                    index_info['metrics'].append(
                                        "{} {{cluster=\"{}\", node=\"{}\", "
                                        "bucket=\"{}\", "
                                        "type=\"index\"}} {} {}".format(
                                            index_type,
                                            cluster_name,
                                            node_hostname,
                                            bucket,
                                            ii_json['op']['samples'][record][samples_count - 1],
                                            ii_json['op']['samples']['timestamp'][samples_count - 1]
                                        )
                                    )
                                else:
                                    for idx, datapoint in enumerate(ii_json['op']['samples'][record]):
                                        if idx in sample_list:
                                            index_info['metrics'].append(
                                                "{} {{cluster=\"{}\", node=\"{}\", "
                                                "bucket=\"{}\", "
                                                "type=\"index\"}} {} {}".format(
                                                    index_type,
                                                    cluster_name,
                                                    node_hostname,
                                                    bucket,
                                                    datapoint,
                                                    ii_json['op']['samples']['timestamp'][idx]
                                                )
                                            )
                            else:
                                index_info['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "bucket=\"{}\", "
                                    "type=\"index\"}} {}".format(
                                        index_type,
                                        cluster_name,
                                        node_hostname,
                                        bucket,
                                        ii_json['op']['samples'][record]
                                    )
                                )
                        else:
                            next
                    except Exception as e:
                        print("index specific: " + str(e))

            except Exception as e:
                print("index: " + str(e))

    return index_info

def _get_index_replica_counts(url, user, passwrd, cluster_name=""):
    '''Get a list of all the indexes and their replica counts'''
    replica_info = {}
    replica_info['metrics'] = []

    auth = basic_authorization(user, passwrd)

    try:
        _url = "http://{}:8091/indexStatus".format(url.split(":")[0])
        result = rest_request(auth, _url)

        for _index in result['indexes']:
            try:
                num_replica = 0
                try:
                    num_replica = _index['numReplica']
                except:
                    pass
                # only output the index_num_replica stat, if we're in cluster mode, or if we're in local mode
                # and the local nodes Couchbase hostname is in the indexes hosts list
                if (application.config['CB_EXPORTER_MODE'] == "local" and url + ":8091" in _index['hosts']) or application.config['CB_EXPORTER_MODE'] == "cluster":
                    replica_info['metrics'].append(
                        "index_num_replica {{cluster=\"{}\", node=\"{}\","
                        "index=\"{}\", "
                        "bucket=\"{}\", "
                        "type=\"index\"}} {}".format(
                            cluster_name,
                            _index['hosts'][0],
                            _index['index'],
                            _index['bucket'],
                            num_replica))

            except Exception as e:
                print("error: {}, {}".format(_index, str(e)))

    except Exception as e:
        print("indexReplicas: {}".format(str(e)))
    return replica_info
