import datetime
import urllib2
import json

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def convert_ip_to_string(ip_address):
    ip_address = ip_address.split(":")[0].replace(".", "_")
    return ip_address

def gt(dt_str):
    print(dt_str)
    dt, _, us= dt_str.partition(".")
    dt= datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    return dt

def basic_authorization(user, password):
    s = user + ":" + password
    return "Basic " + s.encode("base64").rstrip()

def _getCluster(url, user, passwrd, nodeList = []):
    result = {}
    original_nodeLen = len(nodeList)
    if original_nodeLen == 0:
        nodeList.append(url)
    for url in nodeList:
        _url = "http://{}:8091/pools/default".format(url.split(":")[0])
        req = urllib2.Request(_url,
                              headers={
                                  "Authorization": basic_authorization(user, passwrd),
                                  "Content-Type": "application/x-www-form-urlencoded",

                                  # Some extra headers for fun
                                  "Accept": "*/*", # curl does this
                                  "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                              })

        f = (urllib2.urlopen(req)).read()

        node_list = []
        stats = json.loads(f)
        service_nodes = {}
        service_nodes['kv'] = []
        service_nodes['index'] = []
        service_nodes['n1ql'] = []
        service_nodes['eventing'] = []
        service_nodes['fts'] = []
        service_nodes['cbas'] = []


        result['metrics'] = []
        convrt_url = convert_ip_to_string(url)
        for record in stats:
            if original_nodeLen > 0:
                if record == "nodes":
                    for node in stats[record]:
                        try:
                            if node['thisNode']:
                                for metric in node:
                                    if metric in ["thisNode"]:
                                        next
                                    else:
                                        if metric in ["clusterMembership", "recoveryType", "status"]:
                                            if metric == "clusterMembership":
                                                if node[metric] == "active":
                                                    result['metrics'].append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("clusterMembership", convrt_url, 1))
                                                else:
                                                    result['metrics'].append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("clusterMembership", convrt_url, 0))
                                            if metric == "recoveryType":
                                                if node[metric] == "none":
                                                    result['metrics'].append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("recoveryType", convrt_url, 0))
                                                else:
                                                    result['metrics'].append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("recoveryType", convrt_url, 1))
                                            if metric == "status":
                                                if node[metric] == "healthy":
                                                    result['metrics'].append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("status", convrt_url, 1))
                                                else:
                                                    result['metrics'].append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("status", convrt_url, 0))
                                        elif metric in ["ports", "services", "couchApiBase", "couchApiBaseHTTPS", "version", "os", "hostname"]:
                                            next
                                        elif metric == "interestingStats":
                                            for _metric in node[metric]:
                                                result['metrics'].append("{} {{node=\"{}\", type=\"nodes\"}} {}".format(_metric, convrt_url, node[metric][_metric]))
                                        elif metric == "systemStats":
                                            for _metric in node[metric]:
                                                result['metrics'].append("{} {{node=\"{}\", type=\"nodes\"}} {}".format(_metric, convrt_url, node[metric][_metric]))
                                        else:
                                            result['metrics'].append("{} {{node=\"{}\", type=\"nodes\"}} {}".format(metric, convrt_url, node[metric]))
                        except Exception as e:
                            print(e)

            else:
                if record == "nodes":
                    for node in stats[record]:
                        node_list.append(node['hostname'])
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
                    result['nodeList'] = node_list

                elif record in ["rebalanceStatus", "balanced"]:
                    if record == "rebalanceStatus":
                        if stats['rebalanceStatus'] == "none":
                            result['metrics'].append("{} {{type=\"cluster\"}} {}".format(record, 0))
                        else:
                            result['metrics'].append("{} {{type=\"cluster\"}} {}".format(record, 1))
                    elif record == "balanced":
                        if stats[record] == True:
                            result['metrics'].append("{} {{type=\"cluster\"}} {}".format(record, 0))
                        else:
                            result['metrics'].append("{} {{type=\"cluster\"}} {}".format(record, 1))

                elif record in ["autoCompactionSettings"]:
                    for compactionType in stats[record]:
                        if compactionType in ["databaseFragmentationThreshold", "viewFragmentationThreshold"]:
                            for _metric in stats[record][compactionType]:
                                try:
                                    int(stats[record][compactionType][_metric])
                                    result['metrics'].append("{} {{type=\"cluster\"}} {}".format(_metric, stats[record][compactionType][_metric]))
                                except Exception as e:
                                    pass
                elif record in ["counters"]:
                    for counter in stats[record]:
                        result['metrics'].append("{} {{type=\"cluster\"}} {}".format(counter, stats[record][counter]))

                elif record in ["storageTotals"]:
                    for storageType in stats[record]:
                        for _metric in stats[record][storageType]:
                            result['metrics'].append("{}{} {{type=\"cluster\"}} {}".format(storageType, _metric, stats[record][storageType][_metric]))

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
                                "clusterName",
                                "name"]:
                    next
                else:
                    result['metrics'].append("{} {{type=\"cluster\"}} {}".format(record, stats[record]))
    return(result)


def _get_bucket_metrics(url, user, passwrd, nodeList):
    bucket_info = {}
    bucket_info['buckets'] = []
    bucket_info['metrics'] = []
    try:
        _url = "http://{}:8091/pools/default/buckets".format(url)
        req = urllib2.Request(_url,
                              headers={
                                  "Authorization": basic_authorization(user, passwrd),
                                  "Content-Type": "application/x-www-form-urlencoded",

                                  # Some extra headers for fun
                                  "Accept": "*/*", # curl does this
                                  "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                              })

        f = (urllib2.urlopen(req)).read()
        f_json = json.loads(f)
        for node in nodeList:
            for bucket in f_json:
                bucket_info['buckets'].append(bucket['name'])
                bucket_url = "http://{}:8091/pools/default/buckets/{}/nodes/{}/stats".format(url, bucket['name'], node)
                print(bucket_url)
                # print(bucket_url)
                req = urllib2.Request(bucket_url,
                                      headers={
                                          "Authorization": basic_authorization(user, passwrd),
                                          "Content-Type": "application/x-www-form-urlencoded",

                                          # Some extra headers for fun
                                          "Accept": "*/*", # curl does this
                                          "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                                      })

                b = (urllib2.urlopen(req)).read()
                b_json = json.loads(b)
                _node = convert_ip_to_string(node)
                for record in  b_json['op']['samples']:
                    for idx, datapoint in enumerate(b_json['op']['samples'][record]):
                        bucket_info['metrics'].append("{} {{bucket=\"{}\", node=\"{}\", type=\"bucket\"}} {} {}".format(record, bucket['name'], _node, datapoint, b_json['op']['samples']['timestamp'][idx]))
    except Exception as e:
        pass
    return bucket_info



if __name__ == "__main__":
    url = "10.112.192.101"
    user = "Administrator"
    passwrd = "password"

    metrics = []
    clusterValues = _getCluster(url, user, passwrd)
    metrics = clusterValues['metrics']
    nodeMetrics = _getCluster(url, user, passwrd, clusterValues['nodeList'])
    metrics = metrics + nodeMetrics['metrics']

    bucketMetrics = _get_bucket_metrics(url, user, passwrd, clusterValues['nodeList'])

    metrics = metrics + bucketMetrics['metrics']

    for metric in bucketMetrics['metrics']:
        print(metric)
