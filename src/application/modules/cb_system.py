from cb_utilities import *
import cb_cluster, cb_nodes

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "system"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},]
        self.comment = '''This is the method used to access system metrics'''
        self.service_identifier = False

def run(url="", user="", passwrd="", nodes=[]):
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
                cluster_values['nodeList'], cluster_values['clusterName'])
            metrics = metrics + node_metrics['metrics']
            # get system metrics
            cluster_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['nodeList'], cluster_values['clusterName'])
            metrics = metrics + cluster_metrics['metrics']
    else:
        # get node metrics
        node_metrics = cb_nodes._get_metrics(
            user,
            passwrd,
            nodes, cluster_values['clusterName'])
        metrics = metrics + node_metrics['metrics']
        # get system metrics
        cluster_metrics = _get_metrics(
            user,
            passwrd,
            nodes, cluster_values['clusterName'])
        metrics = cluster_metrics['metrics']
    return metrics



def _get_metrics(user, passwrd, node_list, cluster_name=""):
    '''Gets the system stats'''
    system_info = {}
    system_info['metrics'] = []

    auth = basic_authorization(user, passwrd)

    for node in node_list:
        try:
            _query_url = "http://{}:8091/pools/default/buckets/@system/nodes/{}:8091/stats".format(
                node.split(":")[0], node.split(":")[0])
            q_json = rest_request(auth, _query_url)
            _node = value_to_string(node)
            for record in q_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(q_json['op']['samples'][record]):
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
