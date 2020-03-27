from cb_utilities import *
import cb_cluster, cb_nodes

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "system"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},]
        self.comment = '''This is the method used to access system metrics'''
        self.service_identifier = False
        self.inputs = [{"value":"user"},
                        {"value":"passwrd"},
                        {"value":"cluster_values['nodeList']"},
                        {"value":"cluster_values['clusterName']"},
                        {"value":"result_set"}]


def run(url="", user="", passwrd="", nodes=[], result_set=60):
    '''Entry point for getting the metrics for the system from the nodes'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if len(nodes) == 0:
        if len(cluster_values['nodeList']) > 0:
            # get node metrics
            node_metrics = cb_nodes._get_metrics(
                user,
                passwrd,
                cluster_values['nodeList'], cluster_values['clusterName'],
                result_set)
            metrics = metrics + node_metrics['metrics']
            # get system metrics
            cluster_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['nodeList'], cluster_values['clusterName'],
                result_set)
            metrics = metrics + cluster_metrics['metrics']
    else:
        # get node metrics
        node_metrics = cb_nodes._get_metrics(
            user,
            passwrd,
            nodes, cluster_values['clusterName'],
            result_set)
        metrics = metrics + node_metrics['metrics']
        # get system metrics
        cluster_metrics = _get_metrics(
            user,
            passwrd,
            nodes, cluster_values['clusterName'],
            result_set)
        metrics = cluster_metrics['metrics']
    return metrics



def _get_metrics(user, passwrd, node_list, cluster_name="", result_set=60):
    '''Gets the system stats'''
    system_info = {}
    system_info['metrics'] = []

    auth = basic_authorization(user, passwrd)
    sample_list = get_sample_list(result_set)
    for node in node_list:
        try:
            _query_url = "http://{}:8091/pools/default/buckets/@system/nodes/{}:8091/stats".format(
                node.split(":")[0], node.split(":")[0])
            q_json = rest_request(auth, _query_url)
            _node = node
            for record in q_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(q_json['op']['samples'][record]):
                        if idx in sample_list:
                            system_info['metrics'].append(
                                "{} {{cluster=\"{}\", node=\"{}\", "
                                "type=\"system\"}} {} {}".format(
                                    record,
                                    cluster_name,
                                    _node,
                                    datapoint,
                                    q_json['op']['samples']['timestamp'][idx]))

        except Exception as e:
            print("system base: " + str(e))
    return system_info
