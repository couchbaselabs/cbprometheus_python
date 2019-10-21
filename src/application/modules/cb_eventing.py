from cb_utilities import *

def _get_eventing_metrics(user, passwrd, node_list, cluster_name=""):
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
                _node = value_to_string(node)
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