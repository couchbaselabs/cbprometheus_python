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
    service_nodes = {}
    service_nodes['kv'] = []
    service_nodes['index'] = []
    service_nodes['n1ql'] = []
    service_nodes['eventing'] = []
    service_nodes['fts'] = []
    service_nodes['cbas'] = []
    for node in stats['nodes']:
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
    result = {}
    result['serviceNodes'] = service_nodes
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



if __name__ == "__main__":
    url = "10.112.191.101"
    user = "Administrator"
    passwrd = "password1"

    clusterValues = _getCluster(url, user, passwrd)
    for entry in metrics['metrics']:
        print(entry)
