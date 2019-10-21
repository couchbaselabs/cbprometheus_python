from cb_utilities import *

def _get_cbas_metrics(user, passwrd, node_list, cluster_name=""):
    '''Analytics metrics'''
    cbas_metrics = {}
    cbas_metrics['metrics'] = []

    auth = basic_authorization(user, passwrd)

    for node in node_list:
        try:
            _cbas_url = "http://{}:8091/pools/default/buckets/@cbas/nodes/{}:8091/stats".format(
                node.split(":")[0], node.split(":")[0])
            a_json = rest_request(auth, _cbas_url)
            _node = value_to_string(node)
            for record in a_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(
                            a_json['op']['samples'][record]):
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