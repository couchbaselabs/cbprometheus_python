import sys

if sys.version_info[0] == 3:
    from .cb_utilities import *
    from . import cb_cluster, cb_nodes
else:
    from cb_utilities import *
    import cb_cluster, cb_nodes

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "system"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},
                        {"variable":"result_set","type":"int","name":"num_samples","value":60}]
        self.comment = '''This is the method used to access system metrics'''
        self.service_identifier = False
        self.inputs = [{"value":"user"},
                        {"value":"passwrd"},
                        {"value":"cluster_values['nodeList']"},
                        {"value":"cluster_values['clusterName']"},
                        {"value":"result_set"}]
        self.exclude = False


def run(url="", user="", passwrd="", nodes=[], num_samples = 60, result_set=60):
    '''Entry point for getting the metrics for the system from the nodes'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if num_samples != 60:
        result_set = num_samples
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
            # get disk metrics
            disk_metrics = _get_disk_metrics(
                user,
                passwrd,
                cluster_values['nodeList'],
                cluster_values['clusterName'])
            metrics = metrics + disk_metrics['metrics']
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
        metrics = metrics + cluster_metrics['metrics']
        # get disk metrics
        disk_metrics = _get_disk_metrics(
            user,
            passwrd,
            cluster_values['nodeList'],
            cluster_values['clusterName'])
        metrics = metrics + disk_metrics['metrics']
    return metrics


def _get_metrics(user, passwrd, node_list, cluster_name="", result_set=60):
    '''Gets the system stats'''
    system_info = {}
    system_info['metrics'] = []

    auth = basic_authorization(user, passwrd)
    sample_list = get_sample_list(result_set)
    for node in node_list:
        node_hostname = node.split(":")[0]
        try:
            _query_url = "http://{}:8091/pools/default/buckets/@system/nodes/{}:8091/stats".format(
                node_hostname, node_hostname)
            q_json = rest_request(auth, _query_url)
            for record in q_json['op']['samples']:
                samples_count = len(q_json['op']['samples'][record])
                if record != "timestamp":
                    # if the sample list value is greater than the samples count, just use the last sample
                    if samples_count < sample_list[0]:
                        system_info['metrics'].append(
                            "{} {{cluster=\"{}\", node=\"{}\", "
                            "type=\"system\"}} {} {}".format(
                                record,
                                cluster_name,
                                node_hostname,
                                q_json['op']['samples'][record][samples_count - 1],
                                q_json['op']['samples']['timestamp'][samples_count - 1]
                            )
                        )
                    else:
                        for idx, datapoint in enumerate(q_json['op']['samples'][record]):
                            if idx in sample_list:
                                system_info['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "type=\"system\"}} {} {}".format(
                                        record,
                                        cluster_name,
                                        node_hostname,
                                        datapoint,
                                        q_json['op']['samples']['timestamp'][idx]
                                    )
                                )

        except Exception as e:
            print("system base: " + str(e))
    return system_info


def _get_disk_metrics(user, passwrd, node_list, cluster_name=""):
    '''Gets the disk stats'''
    disk_info = {}
    disk_info['metrics'] = []

    auth = basic_authorization(user, passwrd)
    for node in node_list:
        node_hostname = node.split(":")[0]
        try:
            _query_url = "http://{}:8091/nodes/self".format(node_hostname)
            q_json = rest_request(auth, _query_url)
            # loop over each of the available storage types
            for storage_type in q_json['availableStorage']:
                # loop over each disk
                for i, disk in enumerate(q_json['availableStorage'][storage_type]):
                    disk_info['metrics'].append(
                        "disk_usage_bytes {{cluster=\"{}\", node=\"{}\", "
                        "storage_type=\"{}\", path=\"{}\", type=\"system\"}} {}".format(
                            cluster_name,
                            node_hostname,
                            storage_type,
                            disk['path'],
                            disk['sizeKBytes'] * 1000))
                    disk_info['metrics'].append(
                        "disk_usage_percent {{cluster=\"{}\", node=\"{}\", "
                        "storage_type=\"{}\", path=\"{}\", type=\"system\"}} {}".format(
                            cluster_name,
                            node_hostname,
                            storage_type,
                            disk['path'],
                            disk['usagePercent']))

        except Exception as e:
            print("system disk: " + str(e))
    return disk_info
