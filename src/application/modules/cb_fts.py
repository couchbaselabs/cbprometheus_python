from cb_utilities import *

def _get_fts_metrics(user, passwrd, node_list, bucket_list, cluster_name=""):
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