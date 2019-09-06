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

def _get_base_metrics(url, user, passwrd):
    try:

        result = _getCluster(url, user, passwrd)
        metrics = result['metrics']
        for node in result['nodeList']:
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
        metrics_str = "\n"
        metrics_str = metrics_str.join(metrics)
        print(metrics_str)
        return(metrics_str)
    except Exception as e:
        print("Curl Error:", e.args)
        return("")


def get_base_metrics():
    url = "10.112.191.101"
    user = "Administrator"
    passwrd = "password1"
    _value = _get_base_metrics(url, user, passwrd)
    return _value

if __name__ == "__main__":
    get_base_metrics()
