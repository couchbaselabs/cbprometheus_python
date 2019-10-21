from cb_utilities import *

def _get_query_metrics(user, passwrd, node_list, cluster_name=""):
    '''Gets the metrics for the query nodes'''
    query_info = {}
    query_info['metrics'] = []

    auth = basic_authorization(user, passwrd)

    for node in node_list:
        try:
            _query_url = "http://{}:8091/pools/default/buckets/@query/nodes/{}:8091/stats".format(
                node.split(":")[0], node.split(":")[0])
            q_json = rest_request(auth, _query_url)
            _node = value_to_string(node)
            for record in q_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(q_json['op']['samples'][record]):
                        query_info['metrics'].append(
                            "{} {{cluster=\"{}\", node=\"{}\", "
                            "type=\"query\"}} {} {}".format(
                                record,
                                cluster_name,
                                _node,
                                datapoint,
                                q_json['op']['samples']['timestamp'][idx]))

        except Exception as e:
            print("query base: " + str(e))
    return query_info