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

def _getCluster(url, user, passwrd, nodeList):
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
                            if 'thisNode' in node.keys():
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
                            print("buckets: " + str(e))

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
            try:
                for bucket in f_json:
                    bucket_info['buckets'].append(bucket['name'])
                    bucket_url = "http://{}:8091/pools/default/buckets/{}/nodes/{}/stats".format(url, bucket['name'], node)
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

                        if record != "timestamp":
                            if len(record.split("/")) == 3:
                                ddocType = record.split("/")[0]
                                ddocUUID = record.split("/")[1]
                                ddocStat = record.split("/")[2]
                                for idx, datapoint in enumerate(b_json['op']['samples'][record]):
                                    bucket_info['metrics'].append("{} {{bucket=\"{}\", node=\"{}\", type=\"view\" viewType=\"{}\", view=\"{}\"}} {} {}".format(ddocStat, bucket['name'], _node, ddocType, ddocUUID, datapoint, b_json['op']['samples']['timestamp'][idx]))

                            else:
                                for idx, datapoint in enumerate(b_json['op']['samples'][record]):
                                    bucket_info['metrics'].append("{} {{bucket=\"{}\", node=\"{}\", type=\"bucket\"}} {} {}".format(record, bucket['name'], _node, datapoint, b_json['op']['samples']['timestamp'][idx]))
            except Exception as e:
                pass
    except Exception as e:
        pass
    return bucket_info

def _get_index_metrics(url, user, passwrd, nodes, buckets):
    index_info = {}
    index_info['metrics'] = []
    # get cluster index info
    for node in nodes:
        _index_url = "http://{}/pools/default/buckets/@index/nodes/{}/stats".format(node, node)
        try:
            req = urllib2.Request(_index_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*", # curl does this
                                      "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                                  })

            i = (urllib2.urlopen(req)).read()
            i_json = json.loads(i)
            _node = convert_ip_to_string(node)
            for record in i_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(i_json['op']['samples'][record]):
                        index_info['metrics'].append("{} {{node=\"{}\", type=\"index\"}} {} {}".format(record, _node, datapoint, i_json['op']['samples']['timestamp'][idx]))

        except Exception as e:
            print("index base: " + str(e))

    for node in nodes:
        for bucket in buckets:
            try:
                index_info_url = "http://{}/pools/default/buckets/@index-{}/nodes/{}/stats".format(node, bucket, node)
                req = urllib2.Request(index_info_url,
                                      headers={
                                          "Authorization": basic_authorization(user, passwrd),
                                          "Content-Type": "application/x-www-form-urlencoded",

                                          # Some extra headers for fun
                                          "Accept": "*/*", # curl does this
                                          "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                                      })

                ii = (urllib2.urlopen(req)).read()
                ii_json = json.loads(ii)
                for record in ii_json['op']['samples']:
                    name = ""
                    index_type=""
                    stat = ""
                    _node = convert_ip_to_string(node)
                    try:
                        split_record = record.split("/")
                        if len(split_record) == 3:
                            name = (split_record[1]).replace("+", "_")
                            index_type = (split_record[2]).replace("+", "_")
                            if type(ii_json['op']['samples'][record]) == type([]):
                                for idx, datapoint in enumerate(ii_json['op']['samples'][record]):
                                    index_info['metrics'].append("{} {{node = \"{}\", index=\"{}\", bucket=\"{}\", type=\"index_stat\"}} {} {}".format(index_type, _node, name, bucket, datapoint, ii_json['op']['samples']['timestamp'][idx]))
                            else:
                                index_info['metrics'].append("{} {{node = \"{}\", index=\"{}\", bucket=\"{}\", type=\"index_stat\"}} {}".format(index_type, _node, name, bucket, ii_json['op']['samples'][record]))

                        elif len(split_record) == 2:
                            index_type = split_record[1]
                            if type(ii_json['op']['samples'][record]) == type([]):
                                for idx, datapoint in enumerate(ii_json['op']['samples'][record]):
                                    index_info['metrics'].append("{} {{node = \"{}\", bucket=\"{}\", type=\"index_stat\"}} {} {}".format(index_type, _node, bucket, datapoint, ii_json['op']['samples']['timestamp'][idx]))
                            else:
                                index_info['metrics'].append("{} {{node = \"{}\", bucket=\"{}\", type=\"index_stat\"}} {}".format(index_type, _node, bucket, ii_json['op']['samples'][record]))
                        else:
                            next
                    except Exception as e:
                        print("index specific: " + str(e))

            except Exception as e:
                print("index: " + str(e))

    return index_info

def _get_query_metrics(url, user, passwrd, nodeList):
    query_info = {}
    query_info['metrics'] = []

    for node in nodeList:
        try:
            _query_url = "http://{}/pools/default/buckets/@query/nodes/{}/stats".format(node, node)
            req = urllib2.Request(_query_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*", # curl does this
                                      "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                                  })

            q = (urllib2.urlopen(req)).read()
            q_json = json.loads(q)
            _node = convert_ip_to_string(node)
            for record in q_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(q_json['op']['samples'][record]):
                        query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {} {}".format(record, _node, datapoint, q_json['op']['samples']['timestamp'][idx]))

        except Exception as e:
            print("query base: " + str(e))
    return query_info

def _get_eventing_metrics(url, user, passwrd, nodeList):
    eventing_metrics = {}
    eventing_metrics['metrics'] = []

    for node in nodeList:
        try:
            _event_url = "http://{}/pools/default/buckets/@eventing/nodes/{}/stats".format(node, node)
            req = urllib2.Request(_event_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*", # curl does this
                                      "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                                  })

            e = (urllib2.urlopen(req)).read()
            e_json = json.loads(e)
            for record in e_json['op']['samples']:
                name = ""
                metric_type=""
                stat = ""
                _node = convert_ip_to_string(node)
                try:
                    split_record = record.split("/")
                    if len(split_record) == 3:
                        name = (split_record[1]).replace("+", "_")
                        metric_type = (split_record[2]).replace("+", "_")
                        if type(e_json['op']['samples'][record]) == type([]):
                            for idx, datapoint in enumerate(e_json['op']['samples'][record]):
                                eventing_metrics['metrics'].append("{} {{node = \"{}\", function=\"{}\", type=\"eventing_stat\"}} {} {}".format(metric_type, _node, name, datapoint, e_json['op']['samples']['timestamp'][idx]))
                        else:
                            eventing_metrics['metrics'].append("{} {{node = \"{}\", function=\"{}\", type=\"eventing_stat\"}} {}".format(metric_type, _node, name, e_json['op']['samples'][record]))
                    elif len(split_record) == 2:
                        metric_type = (split_record[1]).replace("+", "_")
                        if type(e_json['op']['samples'][record]) == type([]):
                            for idx, datapoint in enumerate(e_json['op']['samples'][record]):
                                eventing_metrics['metrics'].append("{} {{node = \"{}\", type=\"eventing_stat\"}} {} {}".format(metric_type, _node, datapoint, e_json['op']['samples']['timestamp'][idx]))
                        else:
                            eventing_metrics['metrics'].append("{} {{node = \"{}\", type=\"eventing_stat\"}} {}".format(metric_type, _node, datapoint))
                    else:
                        next
                except Exception as e:
                    print("eventing base: " + str(e))
        except Exception as e:
            print("eventing: " + str(e))
    return eventing_metrics

def _get_fts_metrics(url, user, passwrd, nodeList, bucketList):
    fts_metrics = {}
    fts_metrics['metrics'] = []
    for node in nodeList:
        for bucket in bucketList:
            try:
                _fts_url = "http://{}/pools/default/buckets/@fts-{}/nodes/{}/stats".format(node, bucket, node)
                req = urllib2.Request(_fts_url,
                                      headers={
                                          "Authorization": basic_authorization(user, passwrd),
                                          "Content-Type": "application/x-www-form-urlencoded",

                                          # Some extra headers for fun
                                          "Accept": "*/*", # curl does this
                                          "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                                      })

                f = (urllib2.urlopen(req)).read()
                f_json = json.loads(f)
                for record in f_json['op']['samples']:
                    name = ""
                    metric_type=""
                    stat = ""
                    _node = convert_ip_to_string(node)
                    try:
                        split_record = record.split("/")
                        if len(split_record) == 3:
                            name = (split_record[1]).replace("+", "_")
                            metric_type = (split_record[2]).replace("+", "_")
                            if type(f_json['op']['samples'][record]) == type([]):
                                for idx, datapoint in enumerate(f_json['op']['samples'][record]):
                                    fts_metrics['metrics'].append("{} {{node = \"{}\", index=\"{}\", type=\"fts_stat\"}} {} {}".format(metric_type, _node, name, datapoint, f_json['op']['samples']['timestamp'][idx]))
                            else:
                                fts_metrics['metrics'].append("{} {{node = \"{}\", index=\"{}\", type=\"fts_stat\"}} {}".format(metric_type, _node, name, f_json['op']['samples'][record]))
                        elif len(split_record) == 2:
                            metric_type = (split_record[1]).replace("+", "_")
                            if type(f_json['op']['samples'][record]) == type([]):
                                for idx, datapoint in enumerate(f_json['op']['samples'][record]):
                                    fts_metrics['metrics'].append("{} {{node = \"{}\", type=\"fts_stat\"}} {} {}".format(metric_type, _node, datapoint, f_json['op']['samples']['timestamp'][idx]))

                            else:
                                fts_metrics['metrics'].append("{} {{node = \"{}\", type=\"fts_stat\"}} {}".format(metric_type, _node, f_json['op']['samples'][record]))
                        else:
                            next

                    except Exception as e:
                        print("fts base: " + str(e))
            except Exception as e:
                print("fts: " + str(e))
    return fts_metrics

def _get_cbas_metrics(url, user, passwrd, nodeList):
    cbas_metrics = {}
    cbas_metrics['metrics'] = []
    for node in nodeList:
        try:
            _cbas_url = "http://{}/pools/default/buckets/@cbas/nodes/{}/stats".format(node, node)
            req = urllib2.Request(_cbas_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*", # curl does this
                                      "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                                  })

            a = (urllib2.urlopen(req)).read()
            a_json = json.loads(a)
            _node = convert_ip_to_string(node)
            for record in a_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(a_json['op']['samples'][record]):
                        cbas_metrics['metrics'].append("{} {{node = \"{}\", type=\"cbas\"}} {} {}".format(record, _node, datapoint, a_json['op']['samples']['timestamp'][idx]))
        except Exception as e:
            print("analytics base: " + str(e))
    return cbas_metrics

def _get_xdcr_metrics(url, user, passwrd, nodes, buckets):
    xdcr_metrics = {}
    xdcr_metrics['metrics']= []

    try:
        clusterDefinintion = {}
        _remote_cluster_url = "http://{}:8091/pools/default/remoteClusters".format(url)
        req = urllib2.Request(_remote_cluster_url,
                              headers={
                                  "Authorization": basic_authorization(user, passwrd),
                                  "Content-Type": "application/x-www-form-urlencoded",

                                  # Some extra headers for fun
                                  "Accept": "*/*", # curl does this
                                  "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                              })
        _rc = (urllib2.urlopen(req)).read()
        _rc_json = json.loads(_rc)
        for entry in _rc_json:
            clusterDefinintion[entry['uuid']] = {}
            clusterDefinintion[entry['uuid']]['hostname'] = entry['hostname']
            clusterDefinintion[entry['uuid']]['name'] = entry['name']

        try:
            _xdcr_url = "http://{}:8091/pools/default/tasks".format(url)

            req = urllib2.Request(_xdcr_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*", # curl does this
                                      "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                                  })

            _x = (urllib2.urlopen(req)).read()
            _x_json = json.loads(_x)

            #get generic stats for each replication
            for index, record in enumerate(_x_json):
                if record['type']=="xdcr":
                    source = record['source']
                    destBucket = record['target'].split("/")[4]
                    id = record['id'].split("/")[0]
                    hostname = convert_ip_to_string(clusterDefinintion[id]['hostname'])
                    for metric in record:
                        if metric in ["source",
                                      "target",
                                      "id",
                                      "filterExpression",
                                      "continuous",
                                      "settingsURI",
                                      "maxVBReps",
                                      "replicationType",
                                      "type",
                                      "cancelURI"]:
                            next
                        elif metric in ["status",
                                        "pauseRequested",
                                        "errors"]:
                            if metric == "status":
                                if record['status'] == "running":
                                    status = 0
                                elif record['status'] == "paused":
                                    status = 1
                                else:
                                    status = 2
                                xdcr_metrics['metrics'].append("{} {{instanceID=\"{}\", level=\"cluster\", source=\"{}\", destClusterName=\"{}\", destClusterAddress=\"{}\", destBucket=\"{}\", type=\"xdcr\"}} {}".format("status", id, source, clusterDefinintion[id]['name'], hostname, destBucket, status))
                            elif metric == "pauseRequested":
                                if record['pauseRequested']:
                                    pauseRequested = 1
                                else:
                                    pauseRequested = 2
                                xdcr_metrics['metrics'].append("{} {{instanceID=\"{}\", level=\"cluster\", source=\"{}\", destClusterName=\"{}\", destClusterAddress=\"{}\", destBucket=\"{}\", type=\"xdcr\"}} {}".format("pauseRequested", id, source, clusterDefinintion[id]['name'], hostname, destBucket, pauseRequested))
                            elif metric == "errors":
                                xdcr_metrics['metrics'].append("{} {{instanceID=\"{}\", level=\"cluster\", source=\"{}\", destClusterName=\"{}\", destClusterAddress=\"{}\", destBucket=\"{}\", type=\"xdcr\"}} {}".format("errors", id, source, clusterDefinintion[id]['name'], hostname, destBucket, len(record[metric])))
                        else:
                            xdcr_metrics['metrics'].append("{} {{instanceID=\"{}\", level=\"cluster\", source=\"{}\", destClusterName=\"{}\", destClusterAddress=\"{}\", destBucket=\"{}\", type=\"xdcr\"}} {}".format(metric, id, source, clusterDefinintion[id]['name'], hostname, destBucket, record[metric]))
        except Exception as e:
            print("xdcr in: " + str(e))
    except Exception as e:
        print("xcdr out: " + str(e))

    for node in nodes:
        for bucket in buckets:
            try:
                _node_url = "http://{}/pools/default/buckets/@xdcr-{}/nodes/{}/stats".format(node, bucket, node)
                req = urllib2.Request(_node_url,
                                      headers={
                                          "Authorization": basic_authorization(user, passwrd),
                                          "Content-Type": "application/x-www-form-urlencoded",

                                          # Some extra headers for fun
                                          "Accept": "*/*", # curl does this
                                          "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                                      })
                n = (urllib2.urlopen(req)).read()
                n_json = json.loads(n)
                for entry in n_json['op']['samples']:
                    key_split = entry.split("/")
                    if len(key_split) == 5:
                        if entry not in ["timestamp"]:
                            if type(n_json['op']['samples'][entry]) == type([]):
                                for idx, datapoint in enumerate(n_json['op']['samples'][entry]):
                                    xdcr_metrics['metrics'].append("{} {{instanceID=\"{}\", level=\"node\", source=\"{}\", destClusterName=\"{}\", destClusterAddress=\"{}\", destBucket=\"{}\", type=\"xdcr\", node=\"{}\"}} {} {}".format(key_split[4], key_split[1], key_split[2], convert_ip_to_string(clusterDefinintion[key_split[1]]['name']), convert_ip_to_string(clusterDefinintion[key_split[1]]['hostname']), key_split[3], convert_ip_to_string(node), datapoint, n_json['op']['samples']['timestamp'][idx]))
                            elif len(key_split) == 1:
                                for idx, datapoint in enumerate(n_json['op']['samples'][entry]):
                                    xdcr_metrics['metrics'].append("{} {{level=\"bucket\", source=\"{}\", type=\"xdcr\", node=\"{}\"}} {} {}".format(entry, bucket, convert_ip_to_string(node), datapoint, n_json['op']['samples']['timestamp'][idx]))
            except Exception as e:
                print("xdcr: " + str(e))
    return xdcr_metrics

def get_metrics(url="10.112.192.101", user="Administrator", passwrd="password"):
    clusterValues = _getCluster(url, user, passwrd, [])

    metrics = clusterValues['metrics']

    nodeMetrics = _getCluster(url, user, passwrd, clusterValues['nodeList'])
    metrics = metrics + nodeMetrics['metrics']

    if len(clusterValues['serviceNodes']['kv']) > 0:
        bucketMetrics = _get_bucket_metrics(url, user, passwrd, clusterValues['serviceNodes']['kv'])
        metrics = metrics + bucketMetrics['metrics']

    if len(clusterValues['serviceNodes']['index']) > 0 and bucketMetrics['buckets']:
        indexMetrics = _get_index_metrics(url, user, passwrd, clusterValues['serviceNodes']['index'], bucketMetrics['buckets'])
        metrics = metrics + indexMetrics['metrics']

    if len(clusterValues['serviceNodes']['n1ql']) > 0:
        queryMetrics = _get_query_metrics(url, user, passwrd, clusterValues['serviceNodes']['n1ql'])
        metrics = metrics + queryMetrics['metrics']

    if len(clusterValues['serviceNodes']['eventing']) > 0:
        eventingMetrics = _get_eventing_metrics(url, user, passwrd, clusterValues['serviceNodes']['eventing'])
        metrics = metrics + eventingMetrics['metrics']

    if len(clusterValues['serviceNodes']['fts']) > 0:
        ftsMetrics = _get_fts_metrics(url, user, passwrd, clusterValues['serviceNodes']['fts'], bucketMetrics['buckets'])
        metrics = metrics + ftsMetrics['metrics']

    if len(clusterValues['serviceNodes']['cbas']) > 0:
        cbasMetrics = _get_cbas_metrics(url, user, passwrd, clusterValues['serviceNodes']['cbas'])
        metrics = metrics + cbasMetrics['metrics']

    xdcrMetrics = _get_xdcr_metrics(url, user, passwrd, clusterValues['serviceNodes']['kv'], bucketMetrics['buckets'])
    metrics = metrics + cbasMetrics['metrics']

    metrics_str = "\n"
    metrics_str = metrics_str.join(metrics)

    return metrics_str



if __name__ == "__main__":
    url = "10.112.192.101"
    user = "Administrator"
    passwrd = "password"

    get_metrics()
