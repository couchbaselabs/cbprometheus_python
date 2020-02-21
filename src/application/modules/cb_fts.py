from cb_utilities import *
import cb_cluster, cb_bucket

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "fts"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},
                        {"variable":"buckets","type":"default","name":"bucket_list","value":[]}]
        self.comment = '''This is the method used to access FTS metrics'''
        self.service_identifier = "fts"

def run(url="", user="", passwrd="", nodes=[], buckets=[]):
    '''Entry point for getting the metrics for the fts nodes'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])

    if len(nodes) == 0:

        if len(buckets) == 0:
            if len(cluster_values['serviceNodes']['kv']) > 0:
                bucket_metrics = cb_bucket._get_metrics(user,
                                                     passwrd,
                                                     cluster_values['serviceNodes']['kv'],
                                                     cluster_values['clusterName'])
        else:
            bucket_metrics = {"buckets": buckets}

        if len(cluster_values['serviceNodes']['fts']) > 0:
            fts_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['fts'],
                bucket_metrics['buckets'], cluster_values['clusterName'])

            metrics = fts_metrics['metrics']
    else:
        if len(buckets) == 0:
            bucket_metrics = cb_bucket._get_metrics(
                user, passwrd, nodes, cluster_values['clusterName'])
        else:
            bucket_metrics = {"buckets": buckets}

        fts_metrics = _get_metrics(
            user,
            passwrd,
            nodes,
            bucket_metrics['buckets'], cluster_values['clusterName'])

        metrics = fts_metrics['metrics']

    return(metrics)

def _get_metrics(user, passwrd, node_list, bucket_list, cluster_name=""):
    '''gets metrics for FTS'''
    fts_metrics = {}
    fts_metrics['metrics'] = []
    auth = basic_authorization(user, passwrd)

    for node in node_list:
        for bucket in bucket_list:
            try:
                _fts_url = "http://{}:8091/pools/default/buckets/" \
                           "@fts-{}/nodes/{}:8091/stats".format(node.split(":")[0],
                                                                bucket,
                                                                node.split(":")[0])
                f_json = rest_request(auth, _fts_url)
                for record in f_json['op']['samples']:
                    name = ""
                    metric_type = ""
                    _node = value_to_string(node)
                    try:
                        split_record = record.split("/")
                        if len(split_record) == 3:
                            name = (split_record[1]).replace("+", "_")
                            metric_type = (split_record[2]).replace("+", "_")
                            if isinstance(f_json['op']['samples'][record], type([])):
                                for idx, datapoint in enumerate(
                                        f_json['op']['samples'][record]):
                                    fts_metrics['metrics'].append(
                                        "{} {{cluster=\"{}\", node=\"{}\", "
                                        "index=\"{}\", "
                                        "type=\"fts_stat\"}} {} {}".format(
                                            metric_type,
                                            cluster_name,
                                            _node,
                                            name,
                                            datapoint,
                                            f_json['op']['samples']['timestamp'][idx]))
                            else:
                                fts_metrics['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "index=\"{}\", "
                                    "type=\"fts_stat\"}} {}".format(
                                        metric_type,
                                        cluster_name,
                                        _node,
                                        name,
                                        f_json['op']['samples'][record]))
                        elif len(split_record) == 2:
                            metric_type = (split_record[1]).replace("+", "_")
                            if isinstance(f_json['op']['samples'][record], type([])):
                                for idx, datapoint in enumerate(f_json['op']['samples'][record]):
                                    fts_metrics['metrics'].append(
                                        "{} {{cluster=\"{}\", node=\"{}\", "
                                        "type=\"fts_stat\"}} {} {}".format(
                                            metric_type,
                                            cluster_name,
                                            _node,
                                            datapoint,
                                            f_json['op']['samples']['timestamp'][idx]))

                            else:
                                fts_metrics['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "type=\"fts_stat\"}} {}".format(
                                        metric_type,
                                        cluster_name,
                                        _node,
                                        f_json['op']['samples'][record]))
                        else:
                            pass

                    except Exception as e:
                        print("fts base: " + str(e))
            except Exception as e:
                print("fts: " + str(e))
    return fts_metrics
