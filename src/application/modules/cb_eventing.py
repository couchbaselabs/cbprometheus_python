from cb_utilities import *
import cb_cluster

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "eventing"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]}]
        self.comment = '''This is the method used to access Eventing metrics'''
        self.service_identifier = "eventing"
        self.inputs = [{"value":"user"},
                        {"value":"passwrd"},
                        {"value":"cluster_values['serviceNodes']['{}']".format(self.service_identifier)},
                        {"value":"cluster_values['clusterName']"}]
        self.exclude = False


def run(url="", user="", passwrd="", nodes=[]):
    '''Entry point for getting the metrics for the eventing nodes'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])

    if len(nodes) == 0:
        if len(cluster_values['serviceNodes']['eventing']) > 0:
            eventing_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['eventing'], cluster_values['clusterName'])

            metrics = eventing_metrics['metrics']
    else:
        eventing_metrics = _get_metrics(
            user,
            passwrd,
            nodes, cluster_values['clusterName'])

        metrics = eventing_metrics['metrics']

    return metrics

def _get_metrics(user, passwrd, node_list, cluster_name=""):
    '''Gets the metrics for the eventing nodes'''
    eventing_metrics = {}
    eventing_metrics['metrics'] = []
    auth = basic_authorization(user, passwrd)

    for node in node_list:
        try:
            _event_url = "http://{}:8091/pools/default/buckets/" \
                         "@eventing/nodes/{}:8091/stats".format(node.split(":")[0],
                                                                node.split(":")[0])
            e_json = rest_request(auth, _event_url)
            for record in e_json['op']['samples']:
                name = ""
                metric_type = ""
                _node = node
                try:
                    split_record = record.split("/")
                    if len(split_record) == 3:
                        name = (split_record[1]).replace("+", "_")
                        metric_type = (split_record[2]).replace("+", "_")
                        if isinstance(e_json['op']['samples'][record], type([])):
                            for idx, datapoint in enumerate(e_json['op']['samples'][record]):
                                eventing_metrics['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "function=\"{}\", "
                                    "type=\"eventing_stat\"}} {} {}".format(
                                        metric_type,
                                        cluster_name,
                                        _node,
                                        name,
                                        datapoint,
                                        e_json['op']['samples']['timestamp'][idx]))
                        else:
                            eventing_metrics['metrics'].append(
                                "{} {{cluster=\"{}\", node=\"{}\", "
                                "function=\"{}\", "
                                "type=\"eventing_stat\"}} {}".format(
                                    metric_type,
                                    cluster_name,
                                    _node,
                                    name,
                                    e_json['op']['samples'][record]))
                    elif len(split_record) == 2:
                        metric_type = (split_record[1]).replace("+", "_")
                        if isinstance(e_json['op']['samples'][record], type([])):
                            for idx, datapoint in enumerate(
                                    e_json['op']['samples'][record]):
                                eventing_metrics['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "type=\"eventing_stat\"}} {} {}".format(
                                        metric_type,
                                        cluster_name,
                                        _node,
                                        datapoint,
                                        e_json['op']['samples']['timestamp'][idx]))
                        else:
                            eventing_metrics['metrics'].append(
                                "{} {{cluster=\"{}\", node=\"{}\", "
                                "type=\"eventing_stat\"}} {}".format(
                                    metric_type,
                                    cluster_name,
                                    _node,
                                    datapoint))
                    else:
                        next
                except Exception as e:
                    print("eventing base: " + str(e))
        except Exception as e:
            print("eventing: " + str(e))
    return eventing_metrics
