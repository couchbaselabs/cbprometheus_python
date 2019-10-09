#! /usr/bin/python
''''This is the main script for the python exporter for exporting Couchbase RestAPI metrics to Prometheus format.'''

# pylint: disable=C0303, C0325, C1801

import urllib2
import json


def str2bool(v):
    '''Converts string values to boolean'''
    return v.lower() in ("yes", "true", "t", "1")

def value_to_string(ip_address):
    '''converts IP addresses and other values to strings without special characters'''
    ip_address = ip_address.split(":")[0].replace(".", "_").replace("+", "_")
    return ip_address

def basic_authorization(user, password):
    '''Doc String'''
    s = user + ":" + password
    return "Basic " + s.encode("base64").rstrip()

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
    if len(node_list) > 0:
        pass
    else:
        node_list.append(url)

    for uri in node_list:
        try:
            _url = "http://{}:8091/pools/default".format(uri.split(":")[0])
            req = urllib2.Request(_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*",  # curl does this
                                      "User-Agent": "check_version/1",
                                  })

            f = (urllib2.urlopen(req)).read()
            stats = json.loads(f)
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
                            record, 0))
                else:
                    result['metrics'].append(
                        "{} {{type=\"cluster\"}} {}".format(
                            record, 1))
            elif record == "balanced":
                if stats[record]:
                    result['metrics'].append(
                        "{} {{type=\"cluster\"}} {}".format(
                            record, 0))
                else:
                    result['metrics'].append(
                        "{} {{type=\"cluster\"}} {}".format(
                            record, 1))

        elif record in ["autoCompactionSettings"]:
            for compaction_type in stats[record]:
                if compaction_type in ["databaseFragmentationThreshold",
                                       "viewFragmentationThreshold"]:
                    for _metric in stats[record][compaction_type]:
                        try:
                            int(stats[record][compaction_type][_metric])
                            result['metrics'].append(
                                "{} {{type=\"cluster\"}} {}".format(
                                    _metric, stats[record][compaction_type][_metric]))
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
                        storage_type, _metric, stats[record][storage_type][_metric]))

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
            pass
        else:
            result['metrics'].append(
                "{} {{type=\"cluster\"}} {}".format(
                    record, stats[record]))
    return(result)

def _get_node_metrics(user, passwrd, node_list):
    '''gets the metrics for each node'''
    result = {}
    result['metrics'] = []
    for url in node_list:

        try:
            _url = "http://{}:8091/pools/default".format(url.split(":")[0])
            req = urllib2.Request(_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*",  # curl does this
                                      "User-Agent": "check_version/1",
                                  })

            f = (urllib2.urlopen(req)).read()
            stats = json.loads(f)
        except Exception as e:
            print(e)
            return(result)

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
                                                    "{} {{node=\"{}\", type=\"nodes\"}} {}".format(
                                                        metric, convrt_url, 1))
                                            else:
                                                result['metrics'].append(
                                                    "{} {{node=\"{}\", type=\"nodes\"}} {}".format(
                                                        metric, convrt_url, 0))
                                        if metric == "recoveryType":
                                            if node[metric] == "none":
                                                result['metrics'].append(
                                                    "{} {{node=\"{}\", type=\"nodes\"}} {}".format(
                                                        metric, convrt_url, 0))
                                            else:
                                                result['metrics'].append(
                                                    "{} {{node=\"{}\", type=\"nodes\"}} {}".format(
                                                        metric, convrt_url, 1))
                                        if metric == "status":
                                            if node[metric] == "healthy":
                                                result['metrics'].append(
                                                    "{} {{node=\"{}\", type=\"nodes\"}} {}".format(
                                                        metric, convrt_url, 1))
                                            else:
                                                result['metrics'].append(
                                                    "{} {{node=\"{}\", type=\"nodes\"}} {}".format(
                                                        metric, convrt_url, 0))
                                    elif metric in ["ports",
                                                    "services",
                                                    "couchApiBase",
                                                    "couchApiBaseHTTPS",
                                                    "version",
                                                    "os",
                                                    "hostname",
                                                    "otpNode"]:
                                        pass
                                    elif metric == "interestingStats":
                                        for _metric in node[metric]:
                                            result['metrics'].append(
                                                "{} {{node=\"{}\", type=\"nodes\"}} {}".format(
                                                    _metric, convrt_url, node[metric][_metric]))
                                    elif metric == "systemStats":
                                        for _metric in node[metric]:
                                            result['metrics'].append(
                                                "{} {{node=\"{}\", type=\"nodes\"}} {}".format(
                                                    _metric, convrt_url, node[metric][_metric]))
                                    else:
                                        result['metrics'].append(
                                            "{} {{node=\"{}\", type=\"nodes\"}} {}".format(
                                                metric, convrt_url, node[metric]))
                    except Exception as e:
                        print("buckets: " + str(e))

        # else:

    return(result)

def _get_bucket_metrics(user, passwrd, node_list, bucket_names = []):
    '''Gets the metrics for each bucket'''
    bucket_info = {}
    bucket_info['buckets'] = []
    bucket_info['metrics'] = []
    try:
        for uri in node_list:
            try:
                _url = "http://{}:8091/pools/default/buckets".format(uri.split(":")[0])
                print(_url)
                req = urllib2.Request(_url,
                                      headers={
                                          "Authorization": basic_authorization(user, passwrd),
                                          "Content-Type": "application/x-www-form-urlencoded",

                                          # Some extra headers for fun
                                          "Accept": "*/*",  # curl does this
                                          "User-Agent": "check_version/1",
                                      })

                f = (urllib2.urlopen(req)).read()
                f_json = json.loads(f)
                break
            except Exception as e:
                print("Error getting buckets from node: {}: {}".format(uri, str(e.args)))
        for node in node_list:
            try:
                if len(bucket_names) == 0:
                    for bucket in f_json:
                        bucket_info['buckets'].append(bucket['name'])
                        bucket_url = "http://{}:8091/pools/default/buckets/{}/nodes/{}:8091/stats".format(
                            node.split(":")[0], bucket['name'], node.split(":")[0])
                        print(bucket_url)
                        req = urllib2.Request(bucket_url,
                                              headers={
                                                  "Authorization": basic_authorization(user, passwrd),
                                                  "Content-Type": "application/x-www-form-urlencoded",

                                                  # Some extra headers for fun
                                                  "Accept": "*/*",  # curl does this
                                                  "User-Agent": "check_version/1",
                                              })

                        b = (urllib2.urlopen(req)).read()
                        b_json = json.loads(b)
                        _node = value_to_string(node)
                        for _record in b_json['op']['samples']:
                            record = value_to_string(_record)
                            if record != "timestamp":
                                if len(record.split("/")) == 3:
                                    ddoc_type = record.split("/")[0]
                                    ddoc_uuid = record.split("/")[1]
                                    ddoc_stat = record.split("/")[2]
                                    for idx, datapoint in enumerate(b_json['op']['samples'][_record]):
                                        bucket_info['metrics'].append(
                                            "{} {{bucket=\"{}\", "
                                            "node=\"{}\", "
                                            "type=\"view\" "
                                            "viewType=\"{}\", "
                                            "view=\"{}\"}} {} {}".format(
                                                ddoc_stat,
                                                bucket['name'],
                                                _node,
                                                ddoc_type,
                                                ddoc_uuid,
                                                datapoint,
                                                b_json['op']['samples']['timestamp'][idx]))

                                else:
                                    for idx, datapoint in enumerate(b_json['op']['samples'][_record]):
                                        bucket_info['metrics'].append(
                                            "{} {{bucket=\"{}\", "
                                            "node=\"{}\", "
                                            "type=\"bucket\"}} {} {}".format(
                                                record,
                                                bucket['name'],
                                                _node,
                                                datapoint,
                                                b_json['op']['samples']['timestamp'][idx]))
                else:
                    for bucket in bucket_names:
                        bucket_info['buckets'].append(bucket)
                        bucket_url = "http://{}:8091/pools/default/buckets/{}/nodes/{}:8091/stats".format(
                            node.split(":")[0], bucket, node.split(":")[0])
                        print(bucket_url)
                        req = urllib2.Request(bucket_url,
                                              headers={
                                                  "Authorization": basic_authorization(user, passwrd),
                                                  "Content-Type": "application/x-www-form-urlencoded",

                                                  # Some extra headers for fun
                                                  "Accept": "*/*",  # curl does this
                                                  "User-Agent": "check_version/1",
                                              })

                        b = (urllib2.urlopen(req)).read()
                        b_json = json.loads(b)
                        _node = value_to_string(node)
                        for _record in b_json['op']['samples']:
                            record = value_to_string(_record)
                            if record != "timestamp":
                                if len(record.split("/")) == 3:
                                    ddoc_type = record.split("/")[0]
                                    ddoc_uuid = record.split("/")[1]
                                    ddoc_stat = record.split("/")[2]
                                    for idx, datapoint in enumerate(b_json['op']['samples'][_record]):
                                        bucket_info['metrics'].append(
                                            "{} {{bucket=\"{}\", "
                                            "node=\"{}\", "
                                            "type=\"view\" "
                                            "viewType=\"{}\", "
                                            "view=\"{}\"}} {} {}".format(
                                                ddoc_stat,
                                                bucket,
                                                _node,
                                                ddoc_type,
                                                ddoc_uuid,
                                                datapoint,
                                                b_json['op']['samples']['timestamp'][idx]))

                                else:
                                    for idx, datapoint in enumerate(b_json['op']['samples'][_record]):
                                        bucket_info['metrics'].append(
                                            "{} {{bucket=\"{}\", "
                                            "node=\"{}\", "
                                            "type=\"bucket\"}} {} {}".format(
                                                record,
                                                bucket,
                                                _node,
                                                datapoint,
                                                b_json['op']['samples']['timestamp'][idx]))
            except Exception as e:
                print(e)
    except Exception as e:
        pass
    return bucket_info

def _get_index_metrics(user, passwrd, nodes, buckets):
    '''Gets the metrics for the indexes nodes, then gets the metrics for each index'''
    index_info = {}
    index_info['metrics'] = []
    # get cluster index info
    for node in nodes:
        _index_url = "http://{}:8091/pools/default/buckets/@index/nodes/{}:8091/stats".format(
            node.split(":")[0], node.split(":")[0])
        try:
            req = urllib2.Request(_index_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*",  # curl does this
                                      "User-Agent": "check_version/1",
                                  })

            i = (urllib2.urlopen(req)).read()
            i_json = json.loads(i)
            _node = value_to_string(node)
            for record in i_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(i_json['op']['samples'][record]):
                        index_info['metrics'].append(
                            "{} {{node=\"{}\", "
                            "type=\"index-service\"}} {} {}".format(
                                record, _node,
                                datapoint,
                                i_json['op']['samples']['timestamp'][idx]))

        except Exception as e:
            print("index base: " + str(e))

    for node in nodes:
        for bucket in buckets:
            try:
                index_info_url = "http://{}:8091/pools/default/buckets/@index-{}/nodes/{}:8091/stats".format(
                    node.split(":")[0], bucket, node.split(":")[0])
                req = urllib2.Request(index_info_url,
                                      headers={
                                          "Authorization": basic_authorization(user, passwrd),
                                          "Content-Type": "application/x-www-form-urlencoded",

                                          # Some extra headers for fun
                                          "Accept": "*/*",  # curl does this
                                          "User-Agent": "check_version/1",
                                      })

                ii = (urllib2.urlopen(req)).read()
                ii_json = json.loads(ii)
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
                                        "{} {{node = \"{}\","
                                        "index=\"{}\", "
                                        "bucket=\"{}\", "
                                        "type=\"index_stat\"}} {} {}".format(
                                            index_type,
                                            _node,
                                            name,
                                            bucket,
                                            datapoint,
                                            ii_json['op']['samples']['timestamp'][idx]))
                            else:
                                index_info['metrics'].append(
                                    "{} {{node = \"{}\", "
                                    "index=\"{}\", "
                                    "bucket=\"{}\", "
                                    "type=\"index_stat\"}} {}".format(
                                        index_type,
                                        _node,
                                        name,
                                        bucket,
                                        ii_json['op']['samples'][record]))

                        elif len(split_record) == 2:
                            index_type = split_record[1]
                            if isinstance(ii_json['op']['samples'][record], type([])):
                                for idx, datapoint in enumerate(ii_json['op']['samples'][record]):
                                    index_info['metrics'].append(
                                        "{} {{node = \"{}\", "
                                        "bucket=\"{}\", "
                                        "type=\"index_stat\"}} {} {}".format(
                                            index_type,
                                            _node,
                                            bucket,
                                            datapoint,
                                            ii_json['op']['samples']['timestamp'][idx]))
                            else:
                                index_info['metrics'].append(
                                    "{} {{node = \"{}\", "
                                    "bucket=\"{}\", "
                                    "type=\"index_stat\"}} {}".format(
                                        index_type,
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

def _get_query_metrics(user, passwrd, node_list):
    '''Doc String'''
    query_info = {}
    query_info['metrics'] = []

    for node in node_list:
        try:
            _query_url = "http://{}:8091/pools/default/buckets/@query/nodes/{}:8091/stats".format(
                node.split(":")[0], node.split(":")[0])
            req = urllib2.Request(_query_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*",  # curl does this
                                      "User-Agent": "check_version/1",
                                  })

            q = (urllib2.urlopen(req)).read()
            q_json = json.loads(q)
            _node = value_to_string(node)
            for record in q_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(q_json['op']['samples'][record]):
                        query_info['metrics'].append(
                            "{} {{node = \"{}\", "
                            "type=\"query\"}} {} {}".format(
                                record,
                                _node,
                                datapoint,
                                q_json['op']['samples']['timestamp'][idx]))

        except Exception as e:
            print("query base: " + str(e))
    return query_info

def _get_eventing_metrics(user, passwrd, node_list):
    '''Doc String'''
    eventing_metrics = {}
    eventing_metrics['metrics'] = []

    for node in node_list:
        try:
            _event_url = "http://{}:8091/pools/default/buckets/@eventing/nodes/{}:8091/stats".format(
                node.split(":")[0], node.split(":")[0])
            req = urllib2.Request(_event_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*",  # curl does this
                                      "User-Agent": "check_version/1",
                                  })

            e = (urllib2.urlopen(req)).read()
            e_json = json.loads(e)
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
                                    "{} {{node = \"{}\", "
                                    "function=\"{}\", "
                                    "type=\"eventing_stat\"}} {} {}".format(
                                        metric_type,
                                        _node,
                                        name,
                                        datapoint,
                                        e_json['op']['samples']['timestamp'][idx]))
                        else:
                            eventing_metrics['metrics'].append(
                                "{} {{node = \"{}\", "
                                "function=\"{}\", "
                                "type=\"eventing_stat\"}} {}".format(
                                    metric_type,
                                    _node,
                                    name,
                                    e_json['op']['samples'][record]))
                    elif len(split_record) == 2:
                        metric_type = (split_record[1]).replace("+", "_")
                        if isinstance(e_json['op']['samples'][record], type([])):
                            for idx, datapoint in enumerate(
                                    e_json['op']['samples'][record]):
                                eventing_metrics['metrics'].append(
                                    "{} {{node = \"{}\", "
                                    "type=\"eventing_stat\"}} {} {}".format(
                                        metric_type,
                                        _node,
                                        datapoint,
                                        e_json['op']['samples']['timestamp'][idx]))
                        else:
                            eventing_metrics['metrics'].append(
                                "{} {{node = \"{}\", "
                                "type=\"eventing_stat\"}} {}".format(
                                    metric_type,
                                    _node,
                                    datapoint))
                    else:
                        next
                except Exception as e:
                    print("eventing base: " + str(e))
        except Exception as e:
            print("eventing: " + str(e))
    return eventing_metrics

def _get_fts_metrics(user, passwrd, node_list, bucket_list):
    '''gets metrics for FTS'''
    fts_metrics = {}
    fts_metrics['metrics'] = []
    for node in node_list:
        for bucket in bucket_list:
            try:
                _fts_url = "http://{}:8091/pools/default/buckets/@fts-{}/nodes/{}:8091/stats".format(
                    node.split(":")[0], bucket, node.split(":")[0])
                req = urllib2.Request(_fts_url,
                                      headers={
                                          "Authorization": basic_authorization(user, passwrd),
                                          "Content-Type": "application/x-www-form-urlencoded",

                                          # Some extra headers for fun
                                          "Accept": "*/*",  # curl does this
                                          "User-Agent": "check_version/1",
                                      })

                f = (urllib2.urlopen(req)).read()
                f_json = json.loads(f)
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
                                        "{} {{node = \"{}\", "
                                        "index=\"{}\", "
                                        "type=\"fts_stat\"}} {} {}".format(
                                            metric_type,
                                            _node,
                                            name,
                                            datapoint,
                                            f_json['op']['samples']['timestamp'][idx]))
                            else:
                                fts_metrics['metrics'].append(
                                    "{} {{node = \"{}\", "
                                    "index=\"{}\", "
                                    "type=\"fts_stat\"}} {}".format(
                                        metric_type,
                                        _node,
                                        name,
                                        f_json['op']['samples'][record]))
                        elif len(split_record) == 2:
                            metric_type = (split_record[1]).replace("+", "_")
                            if isinstance(f_json['op']['samples'][record], type([])):
                                for idx, datapoint in enumerate(f_json['op']['samples'][record]):
                                    fts_metrics['metrics'].append(
                                        "{} {{node = \"{}\", "
                                        "type=\"fts_stat\"}} {} {}".format(
                                            metric_type,
                                            _node,
                                            datapoint,
                                            f_json['op']['samples']['timestamp'][idx]))

                            else:
                                fts_metrics['metrics'].append(
                                    "{} {{node = \"{}\", "
                                    "type=\"fts_stat\"}} {}".format(
                                        metric_type,
                                        _node,
                                        f_json['op']['samples'][record]))
                        else:
                            pass

                    except Exception as e:
                        print("fts base: " + str(e))
            except Exception as e:
                print("fts: " + str(e))
    return fts_metrics

def _get_cbas_metrics(user, passwrd, node_list):
    '''Analytics metrics'''
    cbas_metrics = {}
    cbas_metrics['metrics'] = []
    for node in node_list:
        try:
            _cbas_url = "http://{}:8091/pools/default/buckets/@cbas/nodes/{}:8091/stats".format(
                node.split(":")[0], node.split(":")[0])
            req = urllib2.Request(_cbas_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*",  # curl does this
                                      "User-Agent": "check_version/1",
                                  })

            a = (urllib2.urlopen(req)).read()
            a_json = json.loads(a)
            _node = value_to_string(node)
            for record in a_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(
                            a_json['op']['samples'][record]):
                        cbas_metrics['metrics'].append(
                            "{} {{node = \"{}\", "
                            "type=\"cbas\"}} {} {}".format(
                                record,
                                _node,
                                datapoint,
                                a_json['op']['samples']['timestamp'][idx]))
        except Exception as e:
            print("analytics base: " + str(e))
    return cbas_metrics

def _get_xdcr_metrics(user, passwrd, nodes, buckets):
    '''XDCR metrics are gatherd here. First the links are queried, then it gathers
    the metrics for each link'''
    xdcr_metrics = {}
    xdcr_metrics['metrics'] = []

    uri = ""
    try:
        for _uri in nodes:
            try:
                cluster_definition = {}
                _remote_cluster_url = "http://{}:8091/pools/default/remoteClusters".format(_uri.split(":")[0])
                req = urllib2.Request(_remote_cluster_url,
                                      headers={
                                          "Authorization": basic_authorization(user, passwrd),
                                          "Content-Type": "application/x-www-form-urlencoded",

                                          # Some extra headers for fun
                                          "Accept": "*/*",  # curl does this
                                          "User-Agent": "check_version/1",
                                      })
                _rc = (urllib2.urlopen(req)).read()
                _rc_json = json.loads(_rc)
                uri = _uri
                break
            except Exception as e:
                print("Error getting xdcr node {}: {}".format(uri, str(e.args)))
        for entry in _rc_json:
            cluster_definition[entry['uuid']] = {}
            cluster_definition[entry['uuid']]['hostname'] = entry['hostname']
            cluster_definition[entry['uuid']]['name'] = entry['name']

        try:
            _xdcr_url = "http://{}:8091/pools/default/tasks".format(uri.split(":")[0])

            req = urllib2.Request(_xdcr_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*",  # curl does this
                                      "User-Agent": "check_version/1",
                                  })

            _x = (urllib2.urlopen(req)).read()
            _x_json = json.loads(_x)

            # get generic stats for each replication
            for record in _x_json:
                if record['type'] == "xdcr":
                    source = record['source']
                    dest_bucket = record['target'].split("/")[4]
                    _id = record['id'].split("/")[0]
                    hostname = value_to_string(cluster_definition[_id]['hostname'])
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
                            pass
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
                                xdcr_metrics['metrics'].append(
                                    "{} {{instanceID=\"{}\", "
                                    "level=\"cluster\", "
                                    "sourceBucket=\"{}\", "
                                    "destClusterName=\"{}\", "
                                    "destClusterAddress=\"{}\", "
                                    "destBucket=\"{}\", "
                                    "type=\"xdcr\"}} {}".format(
                                        "status",
                                        _id,
                                        source,
                                        cluster_definition[id]['name'],
                                        hostname,
                                        dest_bucket,
                                        status))
                            elif metric == "pauseRequested":
                                if record['pauseRequested']:
                                    pause_requested = 1
                                else:
                                    pause_requested = 2
                                xdcr_metrics['metrics'].append(
                                    "{} {{instanceID=\"{}\", "
                                    "level=\"cluster\", "
                                    "source=\"{}\", "
                                    "destClusterName=\"{}\", "
                                    "destClusterAddress=\"{}\", "
                                    "dest_bucket=\"{}\", "
                                    "type=\"xdcr\"}} {}".format(
                                        "pauseRequested",
                                        _id,
                                        source,
                                        cluster_definition[id]['name'],
                                        hostname,
                                        dest_bucket,
                                        pause_requested))
                            elif metric == "errors":
                                xdcr_metrics['metrics'].append(
                                    "{} {{instanceID=\"{}\", "
                                    "level=\"cluster\", "
                                    "source=\"{}\", "
                                    "destClusterName=\"{}\", "
                                    "destClusterAddress=\"{}\", "
                                    "dest_bucket=\"{}\", "
                                    "type=\"xdcr\"}} {}".format(
                                        "errors",
                                        _id,
                                        source,
                                        cluster_definition[id]['name'],
                                        hostname,
                                        dest_bucket,
                                        len(record[metric])))
                        else:
                            xdcr_metrics['metrics'].append(
                                "{} {{instanceID=\"{}\", "
                                "level=\"cluster\", "
                                "source=\"{}\", "
                                "destClusterName=\"{}\", "
                                "destClusterAddress=\"{}\", "
                                "dest_bucket=\"{}\", "
                                "type=\"xdcr\"}} {}".format(
                                    metric,
                                    _id,
                                    source,
                                    cluster_definition[id]['name'],
                                    hostname,
                                    dest_bucket,
                                    record[metric]))
        except Exception as e:
            print("xdcr in: " + str(e))
    except Exception as e:
        print("xcdr out: " + str(e))

    for node in nodes:
        for bucket in buckets:
            try:
                _node_url = "http://{}:8091/pools/default/buckets/@xdcr-{}/nodes/{}:8091/stats".format(
                    node.split(":")[0], bucket, node.split(":")[0])
                req = urllib2.Request(_node_url,
                                      headers={
                                          "Authorization": basic_authorization(user, passwrd),
                                          "Content-Type": "application/x-www-form-urlencoded",

                                          # Some extra headers for fun
                                          "Accept": "*/*",  # curl does this
                                          "User-Agent": "check_version/1",
                                      })
                n = (urllib2.urlopen(req)).read()
                n_json = json.loads(n)
                for entry in n_json['op']['samples']:
                    key_split = entry.split("/")
                    if "timestamp" not in key_split:
                        if len(key_split) == 5:
                            if key_split[4] != "":
                                if isinstance(n_json['op']['samples'][entry], type([])):
                                    for idx, datapoint in enumerate(n_json['op']['samples'][entry]):
                                        xdcr_metrics['metrics'].append(
                                            "{} {{instanceID=\"{}\", "
                                            "level=\"node\", "
                                            "source=\"{}\", "
                                            "destClusterName=\"{}\", "
                                            "destClusterAddress=\"{}\", "
                                            "dest_bucket=\"{}\", "
                                            "type=\"xdcr\", "
                                            "node=\"{}\"}} {} {}".format(
                                                key_split[4],
                                                key_split[1],
                                                key_split[2],
                                                value_to_string(
                                                    cluster_definition[key_split[1]]['name']),
                                                value_to_string(
                                                    cluster_definition[key_split[1]]['hostname']),
                                                key_split[3], value_to_string(node),
                                                datapoint,
                                                n_json['op']['samples']['timestamp'][idx]))
                        elif len(key_split) == 1:
                            for idx, datapoint in enumerate(
                                    n_json['op']['samples'][entry]):
                                xdcr_metrics['metrics'].append(
                                    "{} {{level=\"bucket\", "
                                    "source=\"{}\", "
                                    "type=\"xdcr\", "
                                    "node=\"{}\"}} {} {}".format(
                                        entry,
                                        bucket,
                                        value_to_string(node),
                                        datapoint,
                                        n_json['op']['samples']['timestamp'][idx]))
            except Exception as e:
                print("xdcr: " + str(e))
    return xdcr_metrics

def get_system(url="", user="", passwrd="", nodes=[]):
    metrics = []
    if len(nodes) == 0:
        cluster_values = _get_cluster(url, user, passwrd, [])
        node_metrics = _get_node_metrics(
            user, passwrd, cluster_values['nodeList'])
    else:
        cluster_values = _get_cluster(url, user, passwrd, [])
        node_metrics = _get_node_metrics(
            user, passwrd, nodes)
    metrics = cluster_values['metrics']
    metrics += node_metrics['metrics']

    metrics_str = "\n"
    metrics_str = metrics_str.join(metrics)
    metrics_str += "\n"
    return metrics_str

def get_buckets(url="", user="", passwrd="", buckets=[], nodes=[]):
    metrics = []
    print(buckets)
    if len(nodes) == 0:
        cluster_values = _get_cluster(url, user, passwrd, [])
        if len(cluster_values['serviceNodes']['kv']) > 0:
            bucket_metrics = _get_bucket_metrics(
                user, passwrd, cluster_values['serviceNodes']['kv'], buckets)
            metrics = bucket_metrics['metrics']
    else:
        bucket_metrics = _get_bucket_metrics(
            user, passwrd, nodes, buckets)
        metrics = bucket_metrics['metrics']
    metrics_str = "\n"
    metrics_str = metrics_str.join(metrics)
    metrics_str += "\n"
    return metrics_str

def get_query(url="", user="", passwrd="", nodes=[]):
    metrics = []
    cluster_values = _get_cluster(url, user, passwrd, [])

    if len(nodes) == 0:
        if len(cluster_values['serviceNodes']['n1ql']) > 0:
            query_metrics = _get_query_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['n1ql'])
            metrics = query_metrics['metrics']
    else:
        query_metrics = _get_query_metrics(
            user,
            passwrd,
            nodes)
        metrics = query_metrics['metrics']
    metrics_str = "\n"
    metrics_str = metrics_str.join(metrics)
    metrics_str += "\n"
    return metrics_str

def get_indexes(url="", user="", passwrd="", index="", buckets=[], nodes=[]):
    metrics = []

    if len(nodes) == 0:
        cluster_values = _get_cluster(url, user, passwrd, [])

        if len(buckets) == 0:
            if len(cluster_values['serviceNodes']['kv']) > 0:
                bucket_metrics = _get_bucket_metrics(
                    user, passwrd, cluster_values['serviceNodes']['kv'])
        else:
            bucket_metrics = {"buckets": buckets}

        if len(cluster_values['serviceNodes']['index']) > 0 and bucket_metrics['buckets']:
            index_metrics = _get_index_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['index'],
                bucket_metrics['buckets'])

            metrics = index_metrics['metrics']
    else:
        if len(buckets) == 0:
            bucket_metrics = _get_bucket_metrics(
                user, passwrd, nodes)
        else:
            bucket_metrics = {"buckets": buckets}

        if bucket_metrics['buckets']:
            index_metrics = _get_index_metrics(
                user,
                passwrd,
                nodes,
                bucket_metrics['buckets'])

            metrics = index_metrics['metrics']
    metrics_str = "\n"
    metrics_str = metrics_str.join(metrics)
    metrics_str += "\n"
    return metrics_str

def get_eventing(url="", user="", passwrd="", nodes=[]):
    metrics = []

    if len(nodes) == 0:
        cluster_values = _get_cluster(url, user, passwrd, [])
        if len(cluster_values['serviceNodes']['eventing']) > 0:
            eventing_metrics = _get_eventing_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['eventing'])

            metrics = eventing_metrics['metrics']
    else:
        eventing_metrics = _get_eventing_metrics(
            user,
            passwrd,
            nodes)

        metrics = eventing_metrics['metrics']
    metrics_str = "\n"
    metrics_str = metrics_str.join(metrics)
    metrics_str += "\n"
    return metrics_str

def get_xdcr(url="", user="", passwrd="", nodes=[], buckets=[]):
    metrics = []
    if len(nodes) == 0:
        cluster_values = _get_cluster(url, user, passwrd, [])
        if len(buckets) == 0:
            if len(cluster_values['serviceNodes']['kv']) > 0:
                bucket_metrics = _get_bucket_metrics(
                    user, passwrd, cluster_values['serviceNodes']['kv'])
        else:
            bucket_metrics= {"buckets": buckets}

        xdcr_metrics = _get_xdcr_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['kv'],
            bucket_metrics['buckets'])

        metrics = xdcr_metrics['metrics']

    else:
        if len(buckets) == 0:
            bucket_metrics = _get_bucket_metrics(
                user, passwrd, nodes)
        else:
            bucket_metrics= {"buckets": buckets}

        xdcr_metrics = _get_xdcr_metrics(
            user,
            passwrd,
            nodes,
            bucket_metrics['buckets'])

        metrics = xdcr_metrics['metrics']
    metrics_str = "\n"
    metrics_str = metrics_str.join(metrics)
    metrics_str += "\n"
    return metrics_str

def get_cbas(url="", user="", passwrd="", nodes=[]):
    metrics = []
    if len(nodes) == 0:
        cluster_values = _get_cluster(url, user, passwrd, [])

        if len(cluster_values['serviceNodes']['cbas']) > 0:
            cbas_metrics = _get_cbas_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['cbas'])

        metrics = cbas_metrics['metrics']
    else:
        cbas_metrics = _get_cbas_metrics(
            user,
            passwrd,
            nodes)
        metrics = cbas_metrics['metrics']
    metrics_str = "\n"
    metrics_str = metrics_str.join(metrics)
    metrics_str += "\n"
    return metrics_str

def get_fts(url="", user="", passwrd="", nodes=[], buckets=[]):
    metrics = []
    if len(nodes) == 0:
        cluster_values = _get_cluster(url, user, passwrd, [])

        if len(buckets) == 0:
            if len(cluster_values['serviceNodes']['kv']) > 0:
                bucket_metrics = _get_bucket_metrics(
                user, passwrd, cluster_values['serviceNodes']['kv'])
        else:
            bucket_metrics = {"buckets": buckets}

        if len(cluster_values['serviceNodes']['fts']) > 0:
            fts_metrics = _get_fts_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['fts'],
                bucket_metrics['buckets'])

            metrics = fts_metrics['metrics']
    else:
        if len(buckets) == 0:
            bucket_metrics = _get_bucket_metrics(
                user, passwrd, nodes)
        else:
            bucket_metrics = {"buckets": buckets}

        fts_metrics = _get_fts_metrics(
            user,
            passwrd,
            nodes,
            bucket_metrics['buckets'])

        metrics = fts_metrics['metrics']

    metrics_str = "\n"
    metrics_str = metrics_str.join(metrics)
    metrics_str += "\n"
    return metrics_str

def get_metrics(url="10.112.192.101", user="Administrator", passwrd="password"):
    '''This is the entry point for this script. Gets each type of metric and
    combines them to present'''
    cluster_values = _get_cluster(url, user, passwrd, [])
    metrics = cluster_values['metrics']

    node_metrics = _get_node_metrics(
        user, passwrd, cluster_values['nodeList'])
    metrics = metrics + node_metrics['metrics']

    if len(cluster_values['serviceNodes']['kv']) > 0:
        bucket_metrics = _get_bucket_metrics(
            user, passwrd, cluster_values['serviceNodes']['kv'])
        metrics = metrics + bucket_metrics['metrics']

    if len(cluster_values['serviceNodes']['index']) > 0 and bucket_metrics['buckets']:
        index_metrics = _get_index_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['index'],
            bucket_metrics['buckets'])
        metrics = metrics + index_metrics['metrics']

    if len(cluster_values['serviceNodes']['n1ql']) > 0:
        query_metrics = _get_query_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['n1ql'])
        metrics = metrics + query_metrics['metrics']

    if len(cluster_values['serviceNodes']['eventing']) > 0:
        eventing_metrics = _get_eventing_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['eventing'])
        metrics = metrics + eventing_metrics['metrics']

    if len(cluster_values['serviceNodes']['fts']) > 0:
        fts_metrics = _get_fts_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['fts'],
            bucket_metrics['buckets'])
        metrics = metrics + fts_metrics['metrics']

    if len(cluster_values['serviceNodes']['cbas']) > 0:
        cbas_metrics = _get_cbas_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['cbas'])
        metrics = metrics + cbas_metrics['metrics']

    xdcr_metrics = _get_xdcr_metrics(
        user,
        passwrd,
        cluster_values['serviceNodes']['kv'],
        bucket_metrics['buckets'])
    metrics = metrics + xdcr_metrics['metrics']

    metrics_str = "\n"
    metrics_str = metrics_str.join(metrics)
    return metrics_str

if __name__ == "__main__":
    URL = "10.112.192.101"
    USER = "Administrator"
    PASSWD = "password"

    get_metrics(URL, USER, PASSWD)
