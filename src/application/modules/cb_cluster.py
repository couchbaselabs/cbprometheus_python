from cb_utilities import *

def _get_cluster(url, user, passwrd, node_list):
    '''Starts by getting the cluster definition, then creates a node list, then gets metrics for
    the cluster from each node'''
    result = {}
    result['metrics'] = []
    service_nodes = {}
    service_nodes['kv'] = []
    service_nodes['index'] = []
    service_nodes['n1ql'] = []
    service_nodes['eventing'] = []
    service_nodes['fts'] = []
    service_nodes['cbas'] = []
    current_url = ""
    nodes = []

    auth = basic_authorization(user, passwrd)

    if len(node_list) > 0:
        pass
    else:
        node_list.append(url)

    for uri in node_list:
        print(uri)
        try:
            _url = "http://{}:8091/pools/default".format(uri.split(":")[0])
            stats = rest_request(auth, _url)
            current_url = value_to_string(current_url)
            break
        except Exception as e:
            return (result)

    for record in stats:
        if record == "nodes":
            for node in stats[record]:
                nodes.append(node['hostname'])
                if "kv" in node['services']:
                    service_nodes['kv'].append(node['hostname'])

                if "index" in node['services']:
                    service_nodes['index'].append(node['hostname'])

                if "n1ql" in node['services']:
                    service_nodes['n1ql'].append(node['hostname'])

                if "eventing" in node['services']:
                    service_nodes['eventing'].append(node['hostname'])

                if "fts" in node['services']:
                    service_nodes['fts'].append(node['hostname'])

                if "cbas" in node['services']:
                    service_nodes['cbas'].append(node['hostname'])

            result['serviceNodes'] = service_nodes
            result['nodeList'] = nodes

        elif record in ["rebalanceStatus", "balanced"]:
            if record == "rebalanceStatus":
                if stats['rebalanceStatus'] == "none":
                    result['metrics'].append(
                        "{} {{type=\"cluster\"}} {}".format(
                            snake_caseify(record), 0))
                else:
                    result['metrics'].append(
                        "{} {{type=\"cluster\"}} {}".format(
                            snake_caseify(record), 1))
            elif record == "balanced":
                if stats[record]:
                    result['metrics'].append(
                        "{} {{type=\"cluster\"}} {}".format(
                           snake_caseify(record), 0))
                else:
                    result['metrics'].append(
                        "{} {{type=\"cluster\"}} {}".format(
                            snake_caseify(record), 1))

        elif record in ["autoCompactionSettings"]:
            for compaction_type in stats[record]:
                if compaction_type in ["databaseFragmentationThreshold",
                                       "viewFragmentationThreshold"]:
                    for _metric in stats[record][compaction_type]:
                        try:
                            int(stats[record][compaction_type][_metric])
                            result['metrics'].append(
                                "{} {{type=\"cluster\"}} {}".format(
                                    snake_caseify(_metric), stats[record][compaction_type][_metric]))
                        except Exception as e:
                            pass
        elif record in ["counters"]:
            for counter in stats[record]:
                result['metrics'].append(
                    "{} {{type=\"cluster\"}} {}".format(
                        counter, stats[record][counter]))

        elif record in ["storageTotals"]:
            for storage_type in stats[record]:
                for _metric in stats[record][storage_type]:
                    result['metrics'].append("{}{} {{type=\"cluster\"}} {}".format(
                        storage_type, snake_caseify(_metric), stats[record][storage_type][_metric]))

        elif record in ["clusterName"]:
            result['clusterName'] = stats[record]

        elif record in ["buckets",
                        "remoteClusters",
                        "alerts",
                        "alertsSilenceURL",
                        "controllers",
                        "rebalanceProgressUri",
                        "stopRebalanceUri",
                        "nodeStatusesUri",
                        "tasks",
                        "indexStatusURI",
                        "checkPermissionsURI",
                        "serverGroupsUri",
                        "name"]:
            pass
        else:
            result['metrics'].append(
                "{} {{type=\"cluster\"}} {}".format(
                    snake_caseify(record), stats[record]))

    return(result)
