from cb_utilities import *

def _get_index_metrics(user, passwrd, nodes, buckets, cluster_name=""):
    '''Gets the metrics for the indexes nodes, then gets the metrics for each index'''
    index_info = {}
    index_info['metrics'] = []
    auth = basic_authorization(user, passwrd)

    # get cluster index info
    for node in nodes:
        _index_url = "http://{}:8091/pools/default/buckets/@index/nodes/{}:8091/stats".format(
            node.split(":")[0], node.split(":")[0])
        try:
            i_json = rest_request(auth, _index_url)
            _node = value_to_string(node)
            for record in i_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(i_json['op']['samples'][record]):
                        index_info['metrics'].append(
                            "{} {{cluster=\"{}\", node=\"{}\", "
                            "type=\"index-service\"}} {} {}".format(
                                record,
                                cluster_name,
                                _node,
                                datapoint,
                                i_json['op']['samples']['timestamp'][idx]))

        except Exception as e:
            print("index base: " + str(e))

    for node in nodes:
        for bucket in buckets:
            try:
                index_info_url = "http://{}:8091/pools/default/buckets/@index-{}/" \
                                 "nodes/{}:8091/stats".format(node.split(":")[0],
                                                              bucket,
                                                              node.split(":")[0])
                ii_json = rest_request(auth, index_info_url)
                for record in ii_json['op']['samples']:
                    name = ""
                    index_type = ""
                    _node = value_to_string(node)
                    try:
                        split_record = record.split("/")
                        if len(split_record) == 3:
                            name = (split_record[1]).replace("+", "_")
                            index_type = (split_record[2]).replace("+", "_")
                            if isinstance(ii_json['op']['samples'][record], type([])):
                                for idx, datapoint in enumerate(ii_json['op']['samples'][record]):
                                    index_info['metrics'].append(
                                        "{} {{cluster=\"{}\", node=\"{}\","
                                        "index=\"{}\", "
                                        "bucket=\"{}\", "
                                        "type=\"index\"}} {} {}".format(
                                            index_type,
                                            cluster_name,
                                            _node,
                                            name,
                                            bucket,
                                            datapoint,
                                            ii_json['op']['samples']['timestamp'][idx]))
                            else:
                                index_info['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "index=\"{}\", "
                                    "bucket=\"{}\", "
                                    "type=\"index\"}} {}".format(
                                        index_type,
                                        cluster_name,
                                        _node,
                                        name,
                                        bucket,
                                        ii_json['op']['samples'][record]))

                        elif len(split_record) == 2:
                            index_type = split_record[1]
                            if isinstance(ii_json['op']['samples'][record], type([])):
                                for idx, datapoint in enumerate(ii_json['op']['samples'][record]):
                                    index_info['metrics'].append(
                                        "{} {{cluster=\"{}\", node=\"{}\", "
                                        "bucket=\"{}\", "
                                        "type=\"index\"}} {} {}".format(
                                            index_type,
                                            cluster_name,
                                            _node,
                                            bucket,
                                            datapoint,
                                            ii_json['op']['samples']['timestamp'][idx]))
                            else:
                                index_info['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "bucket=\"{}\", "
                                    "type=\"index\"}} {}".format(
                                        index_type,
                                        cluster_name,
                                        _node,
                                        bucket,
                                        ii_json['op']['samples'][record]))
                        else:
                            next
                    except Exception as e:
                        print("index specific: " + str(e))

            except Exception as e:
                print("index: " + str(e))

    return index_info