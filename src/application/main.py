# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "tdenton"
__date__ = "$Apr 27, 2019 11:29:07 AM$"

import datetime
import urllib2
import json



def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def gt(dt_str):
    print(dt_str)
    dt, _, us= dt_str.partition(".")
    dt= datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    return dt

def basic_authorization(user, password):
    s = user + ":" + password
    return "Basic " + s.encode("base64").rstrip()

def _getCluster(url, user, passwrd):
    _url = "http://{}:8091/pools/default".format(url)
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
    for node in stats['nodes']:
        node_list.append(node['hostname'])
    result = {}
    result['nodeList'] = node_list
    result['metrics'] = []
    try:
        if stats['rebalanceStatus'] == "none":
            result['metrics'].append("{} {{type=\"cluster\"}} {}".format("rebalanceStatus", 0))
        else:
            result['metrics'].append("{} {{type=\"cluster\"}} {}".format("rebalanceStatus", 1))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("maxBucketCount", stats['maxBucketCount']))
    except Exception as e:
        pass
    try:
        int(stats['autoCompactionSettings']['databaseFragmentationThreshold']['percentage'])
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("databaseFragmentationThresholdPercent", stats['autoCompactionSettings']['databaseFragmentationThreshold']['percentage']))
    except Exception as e:
        pass
    try:
        int(stats['autoCompactionSettings']['databaseFragmentationThreshold']['size'])
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("databaseFragmentationThresholdSize", stats['autoCompactionSettings']['databaseFragmentationThreshold']['size']))
    except Exception as e:
        pass

    try:
        int(stats['autoCompactionSettings']['viewFragmentationThreshold']['percentage'])
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("viewFragmentationThresholdPercent", stats['autoCompactionSettings']['viewFragmentationThreshold']['percentage']))
    except Exception as e:
        pass
    try:
        int(stats['autoCompactionSettings']['viewFragmentationThreshold']['size'])
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("viewFragmentationThresholdSize", stats['autoCompactionSettings']['viewFragmentationThreshold']['size']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("indexFragmentationThresholdPercent", stats['autoCompactionSettings']['indexFragmentationThreshold']['percentage']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("indexFragmentationThresholdSize", stats['autoCompactionSettings']['indexFragmentationThreshold']['size']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("rebalanceSuccess", stats['counters']['rebalance_success']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("rebalanceStart", stats['counters']['rebalance_start']))
    except Exception as e:
        pass
    try:
        if stats['balanced'] == True:
            result['metrics'].append("{} {{type=\"cluster\"}} {}".format("balanced", 0))
        else:
            result['metrics'].append("{} {{type=\"cluster\"}} {}".format("balanced", 0))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("memoryQuota", stats['memoryQuota']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("indexMemoryQuota", stats['indexMemoryQuota']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("ftsMemoryQuota", stats['ftsMemoryQuota']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("cbasMemoryQuota", stats['cbasMemoryQuota']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("eventingMemoryQuota", stats['eventingMemoryQuota']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("ramTotal", stats['storageTotal']['ram']['total']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("ramQuotaTotal", stats['storageTotals']['ram']['quotaTotal']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("ramQuotaUsed", stats['storageTotals']['ram']['quotaUsed']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("ramUsed", stats['storageTotals']['ram']['used']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("ramUsedByData", stats['storageTotals']['ram']['usedByData']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("ramQuotaUsedPerNode", stats['storageTotals']['ram']['quotaUsedPerNode']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("ramQuotaTotalPerNode", stats['storageTotals']['ram']['quotaTotalPerNode']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("hddTotal", stats['storageTotals']['hdd']['total']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("hddQuotaTotal", stats['storageTotals']['hdd']['quotaTotal']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("hddUsed", stats['storageTotals']['hdd']['used']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("hddUsedByData", stats['storageTotals']['hdd']['usedByData']))
    except Exception as e:
        pass
    try:
        result['metrics'].append("{} {{type=\"cluster\"}} {}".format("hddFree", stats['storageTotals']['hdd']['free']))
    except Exception as e:
        pass

    return(result)

def _get_base_metrics(url, user, passwrd, nodeList):
    #refactor this to return the metrics and pass the nodelist back in from the main function
    try:
        result = _getCluster(url, user, passwrd)
        metrics = []
        for node in nodeList:
            url = node.split(":")[0]
            _url = "http://{}:8091/pools/default".format(url)
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

            for _node in f_json['nodes']:
                # dashUrl = url.replace(".", "-")
                try:
                    if _node['thisNode']:
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("cpu_utilization_rate", url, _node['systemStats']['cpu_utilization_rate']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("swap_total", url, _node['systemStats']['swap_total']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("swap_used", url, _node['systemStats']['swap_used']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("mem_total", url, _node['systemStats']['mem_total']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("mem_free", url, _node['systemStats']['mem_free']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("cmd_get", url, _node['interestingStats']['cmd_get']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("couch_docs_actual_disk_size", url, _node['interestingStats']['couch_docs_actual_disk_size']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("couch_docs_data_size", url, _node['interestingStats']['couch_docs_data_size']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("couch_spatial_data_size", url, _node['interestingStats']['couch_spatial_data_size']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("couch_spatial_disk_size", url, _node['interestingStats']['couch_spatial_disk_size']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("couch_views_actual_disk_size", url, _node['interestingStats']['couch_views_actual_disk_size']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("couch_views_data_size", url, _node['interestingStats']['couch_views_data_size']))
                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("curr_items", url, _node['interestingStats']['curr_items']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("curr_items_tot", url, _node['interestingStats']['curr_items_tot']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("ep_bg_fetched", url, _node['interestingStats']['ep_bg_fetched']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("get_hits", url, _node['interestingStats']['get_hits']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("mem_used", url, _node['interestingStats']['mem_used']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("ops", url, _node['interestingStats']['ops']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("vb_active_num_non_resident", url, _node['interestingStats']['vb_active_num_non_resident']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("vb_replica_curr_items", url, _node['interestingStats']['vb_replica_curr_items']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("uptime", url, _node['uptime']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("memoryTotal", url, _node['memoryTotal']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("memoryFree", url, _node['memoryFree']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("mcdMemoryReserved", url, _node['mcdMemoryReserved']))

                        except Exception as e:
                            pass
                        try:
                            metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("mcdMemoryAllocated", url, _node['mcdMemoryAllocated']))

                        except Exception as e:
                            pass
                        try:
                            if _node['clusterMembership'] == "active":
                                metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("clusterMembership", url, 1))
                            else:
                                metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("clusterMembership", url, 0))
                        except Exception as e:
                            pass
                        try:
                            if _node['recoveryType'] == "none":
                                metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("recoveryType", url, 0))
                            else:
                                metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("recoveryType", url, 1))
                        except Exception as e:
                            pass
                        try:
                            if _node['status'] == "healthy":
                                metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("status", url, 1))
                            else:
                                metrics.append("{} {{node=\"{}\", type=\"nodes\"}} {}".format("status", url, 1))
                        except Exception as e:
                            pass
                except Exception as e:
                    pass

        return(metrics)
    except Exception as e:
        print("Curl Error:", e.args)
        return("")

def _get_bucket_metrics(url, user, passwrd):
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

        for bucket in f_json:
            bucket_info['buckets'].append(bucket['name'])
            bucket_url = "http://{}:8091/pools/default/buckets/{}/stats?zoom=minute".format(url, bucket['name'])
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
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("mem_used", bucket['name'], sum(b_json['op']['samples']['mem_used']) / len(b_json['op']['samples']['mem_used'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_kv_size", bucket['name'], sum(b_json['op']['samples']['ep_kv_size']) / len(b_json['op']['samples']['ep_kv_size'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_mem_high_wat", bucket['name'], sum(b_json['op']['samples']['ep_mem_high_wat']) / len(b_json['op']['samples']['ep_mem_high_wat'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("mem_total", bucket['name'], sum(b_json['op']['samples']['mem_total']) / len(b_json['op']['samples']['mem_total'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_meta_data_memory", bucket['name'], sum(b_json['op']['samples']['ep_meta_data_memory']) / len(b_json['op']['samples']['ep_meta_data_memory'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_queue_size", bucket['name'], sum(b_json['op']['samples']['ep_queue_size']) / len(b_json['op']['samples']['ep_queue_size'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_flusher_todo", bucket['name'], sum(b_json['op']['samples']['ep_flusher_todo']) / len(b_json['op']['samples']['ep_flusher_todo'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("vb_avg_total_queue_age", bucket['name'], sum(b_json['op']['samples']['vb_avg_total_queue_age']) / len(b_json['op']['samples']['vb_avg_total_queue_age'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_dcp_replica_items_remaining", bucket['name'], sum(b_json['op']['samples']['ep_dcp_replica_items_remaining']) / len(b_json['op']['samples']['ep_dcp_replica_items_remaining'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ops", bucket['name'], sum(b_json['op']['samples']['ops']) / len(b_json['op']['samples']['ops'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("cmd_get", bucket['name'], sum(b_json['op']['samples']['cmd_get']) / len(b_json['op']['samples']['cmd_get'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("cmd_set", bucket['name'], sum(b_json['op']['samples']['cmd_set']) / len(b_json['op']['samples']['cmd_set'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("delete_hits", bucket['name'], sum(b_json['op']['samples']['delete_hits']) / len(b_json['op']['samples']['delete_hits'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_bg_fetched", bucket['name'], sum(b_json['op']['samples']['ep_bg_fetched']) / len(b_json['op']['samples']['ep_bg_fetched'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("curr_connections", bucket['name'], sum(b_json['op']['samples']['curr_connections']) / len(b_json['op']['samples']['curr_connections'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("curr_items", bucket['name'], sum(b_json['op']['samples']['curr_items']) / len(b_json['op']['samples']['curr_items'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("vb_active_resident_items_ratio", bucket['name'], sum(b_json['op']['samples']['vb_active_resident_items_ratio']) / len(b_json['op']['samples']['vb_active_resident_items_ratio'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("vb_replica_resident_items_ratio", bucket['name'], sum(b_json['op']['samples']['vb_replica_resident_items_ratio']) / len(b_json['op']['samples']['vb_replica_resident_items_ratio'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_tmp_oom_errors", bucket['name'], sum(b_json['op']['samples']['ep_tmp_oom_errors']) / len(b_json['op']['samples']['ep_tmp_oom_errors'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_dcp_views_items_remaining", bucket['name'], sum(b_json['op']['samples']['ep_dcp_views_items_remaining']) / len(b_json['op']['samples']['ep_dcp_views_items_remaining'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_dcp_2i_items_remaining", bucket['name'], sum(b_json['op']['samples']['ep_queue_size']) / len(b_json['op']['samples']['ep_queue_size'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_dcp_replica_backoff", bucket['name'], sum(b_json['op']['samples']['ep_dcp_replica_backoff']) / len(b_json['op']['samples']['ep_dcp_replica_backoff'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("ep_dcp_xdcr_backoff", bucket['name'], sum(b_json['op']['samples']['ep_dcp_xdcr_backoff']) / len(b_json['op']['samples']['ep_dcp_xdcr_backoff'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("couch_docs_fragmentation", bucket['name'], sum(b_json['op']['samples']['couch_docs_fragmentation']) / len(b_json['op']['samples']['couch_docs_fragmentation'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("couch_views_fragmentation", bucket['name'], sum(b_json['op']['samples']['couch_views_fragmentation']) / len(b_json['op']['samples']['couch_views_fragmentation'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("vb_replica_num", bucket['name'], sum(b_json['op']['samples']['vb_replica_num']) / len(b_json['op']['samples']['vb_replica_num'])))
            bucket_info['metrics'].append("{} {{bucket=\"{}\", type=\"bucket\"}} {}".format("vb_active_num", bucket['name'], sum(b_json['op']['samples']['vb_active_num']) / len(b_json['op']['samples']['vb_active_num'])))

        return bucket_info
    except Exception as e:
        print(e)
        return []

#Probably dont need to do this as it doesnt really get us anything useful
def _get_view_metrics(url, user, passwrd, bucketList):
    viewInfo = {}
    viewInfo['definitions'] = []
    for bucket in bucketList:
        viewInfo[bucket] = []
        view_url = "http://{}:8091/pools/default/buckets/{}/ddocs".format(url, bucket)
        req = urllib2.Request(view_url,
              headers={
                  "Authorization": basic_authorization(user, passwrd),
                  "Content-Type": "application/x-www-form-urlencoded",

                  # Some extra headers for fun
                  "Accept": "*/*", # curl does this
              })
        try:
            v = (urllib2.urlopen(req)).read()
            v_json = json.loads(v)
            for ddoc in v_json['rows']:
                id = ddoc['doc']['meta']['id']
                try:
                    for _doc in ddoc['doc']['json']['spatial']:
                        definition = {}
                        definition['id'] = id
                        definition['bucket'] = bucket
                        definition['name'] = _doc
                        definition['type'] = "spatial"
                        viewInfo['definitions'].append(definition)
                except Exception as e:
                    for _doc in ddoc['doc']['json']['views']:
                        definition = {}
                        definition['id'] = id
                        definition['bucket'] = bucket
                        definition['name'] = _doc
                        definition['type'] = "views"
                        viewInfo['definitions'].append(definition)
        except Exception as e:
            pass

    for definition in viewInfo['definitions']:
        if definition['type'] == "spatial":
            viewUrl = "http://{}:8092/{}/{}/_spatial/{}".format(url, bucket, definition['id'], definition['name'])
        elif definition['type'] == "views":
            viewUrl = "http://{}:8092/{}/{}/_views/{}".format(url, bucket, definition['id'], definition['name'])
        print(viewUrl)
    metrics = []
    return metrics

def _get_index_metrics(url, user, passwrd, nodes):
    index_info = {}
    index_info['metrics'] = []

    # get cluster index info
    for node in nodes:
        _index_url = " http://{}/pools/default/buckets/@index/nodes/{}/stats".format(node, node)
        try:
            req = urllib2.Request(_index_url,
                  headers={
                      "Authorization": basic_authorization(user, passwrd),
                      "Content-Type": "application/x-www-form-urlencoded",

                      # Some extra headers for fun
                      "Accept": "*/*", # curl does this
                      "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                  })

            _i = (urllib2.urlopen(req)).read()
            _i_json = json.loads(_i)
            index_info['metrics'].append("{} {{node = \"{}\", type=\"index\"}} {}".format("index_ram_percent", node.split(":")[0], sum(_i_json['op']['samples']['index_ram_percent']) / len(_i_json['op']['samples']['index_ram_percent'])))
            index_info['metrics'].append("{} {{node = \"{}\", type=\"index\"}} {}".format("index_memory_used", node.split(":")[0],  sum(_i_json['op']['samples']['index_memory_used']) / len(_i_json['op']['samples']['index_memory_used'])))
            index_info['metrics'].append("{} {{node = \"{}\", type=\"index\"}} {}".format("index_memory_quota", node.split(":")[0], sum(_i_json['op']['samples']['index_memory_quota']) / len(_i_json['op']['samples']['index_memory_quota'])))
            index_info['metrics'].append("{} {{node = \"{}\", type=\"index\"}} {}".format("index_remaining_ram", node.split(":")[0], sum(_i_json['op']['samples']['index_remaining_ram']) / len(_i_json['op']['samples']['index_remaining_ram'])))
        except Exception as e:
            pass

    try:
        for node in nodes:
            index_info_url = "http://{}/pools/default/buckets/@index-main/stats".format(nodes[0])
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
                _node = node.split(":")[0]
                try:
                    split_record = record.split("/")

                    if len(split_record) == 3:
                        name = (split_record[1]).replace("+", "_")
                        index_type = (split_record[2]).replace("+", "_")
                        if type(ii_json['op']['samples'][record]) == type([]):
                            stat = sum(ii_json['op']['samples'][record]) / len(ii_json['op']['samples'][record])
                        else:
                            stat = ii_json['op']['samples'][record]

                        index_info['metrics'].append("{} {{node = \"{}\", index=\"{}\", type=\"index_stat\"}} {}".format(index_type, _node, name, stat))
                    elif len(split_record) == 2:
                        index_type = split_record[1]
                        if type(ii_json['op']['samples'][record]) == type([]):
                            stat = sum(ii_json['op']['samples'][record]) / len(ii_json['op']['samples'][record])
                        else:
                            stat = ii_json['op']['samples'][record]
                        index_info['metrics'].append("{} {{node = \"{}\", type=\"index_stat\"}} {}".format(index_type, _node, stat))
                    else:
                        next


                except Exception as e:
                    print(e)

    except Exception as e:
        print(e)

    return index_info

def _get_query_metrics(url, user, passwrd, nodeList):
    query_info = {}
    query_info['metrics'] = []
    try:
        for node in nodeList:
            _query_url = "http://{}/pools/default/buckets/@query/nodes/{}/stats".format(node, node)
            req = urllib2.Request(_query_url,
                                  headers={
                                      "Authorization": basic_authorization(user, passwrd),
                                      "Content-Type": "application/x-www-form-urlencoded",

                                      # Some extra headers for fun
                                      "Accept": "*/*", # curl does this
                                      "User-Agent": "check_version/1", # otherwise it uses "Python-urllib/..."
                                  })

            _q = (urllib2.urlopen(req)).read()
            _q_json = json.loads(_q)
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_warnings", node.split(":")[0], sum(_q_json['op']['samples']['query_warnings']) / len(_q_json['op']['samples']['query_warnings'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_request_time", node.split(":")[0], sum(_q_json['op']['samples']['query_request_time']) / len(_q_json['op']['samples']['query_request_time'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_result_count", node.split(":")[0], sum(_q_json['op']['samples']['query_result_count']) / len(_q_json['op']['samples']['query_result_count'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_selects", node.split(":")[0], sum(_q_json['op']['samples']['query_selects']) / len(_q_json['op']['samples']['query_selects'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_requests_500ms", node.split(":")[0], sum(_q_json['op']['samples']['query_requests_500ms']) / len(_q_json['op']['samples']['query_requests_500ms'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_active_requests", node.split(":")[0], sum(_q_json['op']['samples']['query_active_requests']) / len(_q_json['op']['samples']['query_active_requests'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_requests_5000ms", node.split(":")[0], sum(_q_json['op']['samples']['query_requests_5000ms']) / len(_q_json['op']['samples']['query_requests_5000ms'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_requests_1000ms", node.split(":")[0], sum(_q_json['op']['samples']['query_requests_1000ms']) / len(_q_json['op']['samples']['query_requests_1000ms'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_invalid_requests", node.split(":")[0], sum(_q_json['op']['samples']['query_invalid_requests']) / len(_q_json['op']['samples']['query_invalid_requests'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_queued_requests", node.split(":")[0], sum(_q_json['op']['samples']['query_queued_requests']) / len(_q_json['op']['samples']['query_queued_requests'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_avg_result_count", node.split(":")[0], sum(_q_json['op']['samples']['query_avg_result_count']) / len(_q_json['op']['samples']['query_avg_result_count'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_service_time", node.split(":")[0], sum(_q_json['op']['samples']['query_service_time']) / len(_q_json['op']['samples']['query_service_time'])))
            # query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("timestamp", node.split(":")[0], sum(_q_json['op']['samples']['timestamp']) / len(_q_json['op']['samples']['timestamp'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_avg_svc_time", node.split(":")[0], sum(_q_json['op']['samples']['query_avg_svc_time']) / len(_q_json['op']['samples']['query_avg_svc_time'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_errors", node.split(":")[0], sum(_q_json['op']['samples']['query_errors']) / len(_q_json['op']['samples']['query_errors'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_requests", node.split(":")[0], sum(_q_json['op']['samples']['query_requests']) / len(_q_json['op']['samples']['query_requests'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_avg_response_size", node.split(":")[0], sum(_q_json['op']['samples']['query_avg_response_size']) / len(_q_json['op']['samples']['query_avg_response_size'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_result_size", node.split(":")[0], sum(_q_json['op']['samples']['query_result_size']) / len(_q_json['op']['samples']['query_result_size'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_avg_req_time", node.split(":")[0], sum(_q_json['op']['samples']['query_avg_req_time']) / len(_q_json['op']['samples']['query_avg_req_time'])))
            query_info['metrics'].append("{} {{node = \"{}\", type=\"query\"}} {}".format("query_requests_250ms", node.split(":")[0], sum(_q_json['op']['samples']['query_requests_250ms']) / len(_q_json['op']['samples']['query_requests_250ms'])))

            # for metric in query_info['metrics']:
            #     print(metric)
    except Exception as e:
        print(e)
    return query_info

def _get_analytics_metrics(url, user, passwrd):
    metrics = []
    return metrics

def _get_eventing_metrics(url, user, passwrd):
    metrics = []
    return metrics

def _get_fts_metrics(url, user, passwrd):
    metrics = []
    return metrics

def get_metrics():
    url = "10.112.191.101"
    user = "Administrator"
    passwrd = "password1"

    clusterValues = _getCluster(url, user, passwrd)
    metrics = clusterValues['metrics']

    node_metrics = _get_base_metrics(url, user, passwrd, clusterValues['nodeList'])
    metrics = metrics + node_metrics

    bucket_metrics = _get_bucket_metrics(url, user, passwrd)
    metrics = metrics + bucket_metrics['metrics']

    # view_metrics = _get_view_metrics(url, user, passwrd, bucket_metrics['buckets'])
    # metrics = metrics + view_metrics

    index_metrics = _get_index_metrics(url, user, passwrd, clusterValues['nodeList'])
    metrics = metrics + index_metrics['metrics']

    query_metrics = _get_query_metrics(url, user, passwrd, clusterValues['nodeList'])
    metrics = metrics + query_metrics['metrics']

    analytics_metrics = _get_analytics_metrics(url, user, passwrd)
    metrics = metrics + analytics_metrics

    eventing_metrics = _get_eventing_metrics(url, user, passwrd)
    metrics = metrics + eventing_metrics

    fts_metrics = _get_fts_metrics(url, user, passwrd)
    metrics = metrics + fts_metrics

    metrics_str = "\n"
    metrics_str = metrics_str.join(metrics)

    return metrics_str

if __name__ == "__main__":
    url = "10.112.191.101"
    user = "Administrator"
    passwrd = "password1"

    clusterValues = _getCluster(url, user, passwrd)
    metrics = _get_query_metrics(url, user, passwrd, clusterValues['nodeList'])
    print(metrics['metrics'])