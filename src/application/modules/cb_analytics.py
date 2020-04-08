from cb_utilities import *
import cb_cluster

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "analytics"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},
                        {"variable":"num_samples","type":"int","name":"num_samples","value":60}]
        self.comment = '''This is the method used to access FTS metrics'''
        self.service_identifier = "cbas"
        self.inputs = [{"value":"user"},
                        {"value":"passwrd"},
                        {"value":"cluster_values['serviceNodes']['{}']".format(self.service_identifier)},
                        {"value":"cluster_values['clusterName']"},
                        {"value":"result_set"}]


def run(url="", user="", passwrd="", nodes=[], num_samples = 60, result_set=60):
    '''Entry point for getting the metrics for the analytics nodes'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if num_samples != 60:
        result_set = num_samples
    if len(nodes) == 0:

        if len(cluster_values['serviceNodes']['cbas']) > 0:
            cbas_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['cbas'], cluster_values['clusterName'],
                result_set)

            metrics = cbas_metrics['metrics']
    else:
        cbas_metrics = _get_metrics(
            user,
            passwrd,
            nodes, cluster_values['clusterName'],
            result_set)
        metrics = cbas_metrics['metrics']

    return metrics

def _get_metrics(user, passwrd, node_list, cluster_name="", result_set=60):
    '''Analytics metrics'''
    cbas_metrics = {}
    cbas_metrics['metrics'] = []

    auth = basic_authorization(user, passwrd)
    sample_list = get_sample_list(result_set)
    for node in node_list:
        try:
            _cbas_url = "http://{}:8091/pools/default/buckets/@cbas/nodes/{}:8091/stats".format(
                node.split(":")[0], node.split(":")[0])
            a_json = rest_request(auth, _cbas_url)
            _node = node
            for record in a_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(
                            a_json['op']['samples'][record]):
                        if idx in sample_list:
                            cbas_metrics['metrics'].append(
                                "{} {{cluster=\"{}\", node=\"{}\", "
                                "type=\"cbas\"}} {} {}".format(
                                    record,
                                    cluster_name,
                                    _node,
                                    datapoint,
                                    a_json['op']['samples']['timestamp'][idx]))
        except Exception as e:
            print("analytics base: " + str(e))
    return cbas_metrics
