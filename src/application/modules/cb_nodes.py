from cb_utilities import *

def _get_node_metrics(user, passwrd, node_list, cluster_name):
    '''gets the metrics for each node'''
    result = {}
    result['metrics'] = []
    auth = basic_authorization(user, passwrd)

    for url in node_list:

        try:
            _url = "http://{}:8091/pools/default".format(url.split(":")[0])
            stats = rest_request(auth, _url)
        except Exception as e:
            print(e)
            return(result)

        metric_renamer = {}
        metric_renamer['clusterMembership'] = "cluster_membership"
        metric_renamer['mcdMemoryReserved'] = "mcd_memory_reserved"
        metric_renamer['cpuCount'] = "cpu_count"
        metric_renamer['clusterCompatibility'] = "cluster_compatibility"
        metric_renamer['mcdMemoryAllocated'] = "mcd_memory_allocated"
        metric_renamer['recoveryType'] = "recovery_type"
        metric_renamer['mcdMemoryReserved'] = "mcd_memory_reserved"
        convrt_url = value_to_string(url)
        for _record in stats:
            record = value_to_string(_record)
            if record == "nodes":
                for node in stats[record]:
                    try:
                        if 'thisNode' in node.keys():
                            for _metric in node:
                                metric = value_to_string(_metric)
                                if metric in ["thisNode"]:
                                    pass
                                else:
                                    if metric in [
                                        "clusterMembership", "recoveryType", "status"]:
                                        if metric == "clusterMembership":
                                            if node[metric] == "active":
                                                result['metrics'].append(
                                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                                    "type=\"node\"}} {}".format(
                                                        metric_renamer.get(metric, metric), cluster_name, convrt_url, 1))
                                            else:
                                                result['metrics'].append(
                                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                                    "type=\"node\"}} {}".format(
                                                        metric_renamer.get(metric, metric), cluster_name, convrt_url, 0))
                                        if metric == "recoveryType":
                                            if node[metric] == "none":
                                                result['metrics'].append(
                                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                                    "type=\"node\"}} {}".format(
                                                        metric_renamer.get(metric, metric), cluster_name, convrt_url, 0))
                                            else:
                                                result['metrics'].append(
                                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                                    "type=\"node\"}} {}".format(
                                                        metric_renamer.get(metric, metric), cluster_name, convrt_url, 1))
                                        if metric == "status":
                                            if node[metric] == "healthy":
                                                result['metrics'].append(
                                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                                    "type=\"node\"}} {}".format(
                                                        metric_renamer.get(metric, metric), cluster_name, convrt_url, 1))
                                            else:
                                                result['metrics'].append(
                                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                                    "type=\"node\"}} {}".format(
                                                        metric_renamer.get(metric, metric), cluster_name, convrt_url, 0))
                                    elif metric in ["ports",
                                                    "services",
                                                    "couchApiBase",
                                                    "couchApiBaseHTTPS",
                                                    "version",
                                                    "os",
                                                    "hostname",
                                                    "otpNode",
                                                    "memoryFree", # this is a duplicate from systemStats.mem_free
                                                    "memoryTotal"  # this is a duplicate from systemStats.mem_total
                                                    ]:
                                        pass
                                    elif metric == "interestingStats":
                                        for _metric in node[metric]:
                                            result['metrics'].append(
                                                "{} {{cluster=\"{}\", node=\"{}\", "
                                                "type=\"node\"}} {}".format(
                                                    _metric,
                                                    cluster_name,
                                                    convrt_url,
                                                    node[metric][_metric]))
                                    elif metric == "systemStats":
                                        for _metric in node[metric]:
                                            result['metrics'].append(
                                                "{} {{cluster=\"{}\", node=\"{}\", "
                                                "type=\"node\"}} {}".format(
                                                    _metric,
                                                    cluster_name,
                                                    convrt_url,
                                                    node[metric][_metric]))
                                    else:
                                        result['metrics'].append(
                                            "{} {{cluster=\"{}\", node=\"{}\", "
                                            "type=\"node\"}} {}".format(
                                                metric_renamer.get(metric, metric),
                                                cluster_name,
                                                convrt_url,
                                                node[metric]))
                    except Exception as e:
                        print("buckets: " + str(e))

    return(result)