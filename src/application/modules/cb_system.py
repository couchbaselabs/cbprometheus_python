from cb_utilities import *

def _get_system_metrics(user, passwrd, node_list, cluster_name=""):
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
