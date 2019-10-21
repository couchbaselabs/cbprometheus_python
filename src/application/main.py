#! /usr/bin/python
''''This is the main script for the python exporter for exporting Couchbase
RestAPI metrics to Prometheus format.'''

# pylint: disable=C0303, C0325, C1801

from modules import cb_analytics, cb_bucket, cb_cluster, cb_eventing, cb_fts, cb_index, cb_nodes, \
    cb_query, cb_system, cb_xdcr


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

def get_system(url="", user="", passwrd="", nodes=[]):
    '''Entry point for getting the metrics for the system from the nodes'''
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if len(nodes) == 0:
        if len(cluster_values['nodeList']) > 0:
            cluster_metrics = cb_system._get_system_metrics(
                user,
                passwrd,
                cluster_values['nodeList'], cluster_values['clusterName'])
            metrics = cluster_metrics['metrics']
    else:
        cluster_metrics = cb_system._get_system_metrics(
            user,
            passwrd,
            nodes, cluster_values['clusterName'])
        metrics = cluster_metrics['metrics']
    return metrics

def get_buckets(url="", user="", passwrd="", buckets=[], nodes=[]):
    '''Entry point for getting the metrics for the kv nodes and buckets'''
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if len(nodes) == 0:
        if len(cluster_values['serviceNodes']['kv']) > 0:
            bucket_metrics = cb_bucket._get_bucket_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['kv'],
                cluster_values['clusterName'],
                buckets)
            metrics = bucket_metrics['metrics']
    else:
        bucket_metrics = cb_bucket._get_bucket_metrics(
            user, passwrd, nodes, cluster_values['clusterName'], buckets)
        metrics = bucket_metrics['metrics']
    return metrics

def get_query(url="", user="", passwrd="", nodes=[]):
    '''Entry point for getting the metrics for the query nodes'''
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])

    if len(nodes) == 0:
        if len(cluster_values['serviceNodes']['n1ql']) > 0:
            query_metrics = cb_query._get_query_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['n1ql'], cluster_values['clusterName'])
            metrics = query_metrics['metrics']
    else:
        query_metrics = cb_query._get_query_metrics(
            user,
            passwrd,
            nodes, cluster_values['clusterName'])
        metrics = query_metrics['metrics']
    return metrics

def get_indexes(url="", user="", passwrd="", index=[], buckets=[], nodes=[]):
    '''Entry point for getting the metrics for the index nodes'''
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if len(buckets) == 0:
        buckets = cb_bucket._get_index_buckets(url, user, passwrd)

    if len(nodes) == 0:

        if len(cluster_values['serviceNodes']['index']) > 0 and len(buckets) > 0:
            index_metrics = cb_index._get_index_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['index'],
                buckets, cluster_values['clusterName'])

            metrics = index_metrics['metrics']
    else:

        if len(buckets) > 0:
            index_metrics = cb_index._get_index_metrics(
                user,
                passwrd,
                nodes,
                buckets, cluster_values['clusterName'])

            metrics = index_metrics['metrics']

    return metrics

def get_eventing(url="", user="", passwrd="", nodes=[]):
    '''Entry point for getting the metrics for the eventing nodes'''
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])

    if len(nodes) == 0:
        if len(cluster_values['serviceNodes']['eventing']) > 0:
            eventing_metrics = cb_eventing._get_eventing_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['eventing'], cluster_values['clusterName'])

            metrics = eventing_metrics['metrics']
    else:
        eventing_metrics = cb_eventing._get_eventing_metrics(
            user,
            passwrd,
            nodes, cluster_values['clusterName'])

        metrics = eventing_metrics['metrics']

    return metrics

def get_xdcr(url="", user="", passwrd="", nodes=[], buckets=[]):
    '''Entry point for getting the metrics for xdcr'''
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])

    if len(nodes) == 0:
        if len(buckets) == 0:
            if len(cluster_values['serviceNodes']['kv']) > 0:
                bucket_metrics = cb_bucket._get_bucket_metrics(
                    user,
                    passwrd,
                    cluster_values['serviceNodes']['kv'],
                    cluster_values['clusterName'])
        else:
            bucket_metrics = {"buckets": buckets}

        xdcr_metrics = cb_xdcr._get_xdcr_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['kv'],
            bucket_metrics['buckets'], cluster_values['clusterName'])

        metrics = xdcr_metrics['metrics']

    else:
        if len(buckets) == 0:
            bucket_metrics = cb_bucket._get_bucket_metrics(
                user, passwrd, nodes, cluster_values['clusterName'])
        else:
            bucket_metrics = {"buckets": buckets}

        xdcr_metrics = cb_xdcr._get_xdcr_metrics(
            user,
            passwrd,
            nodes,
            bucket_metrics['buckets'], cluster_values['clusterName'])

        metrics = xdcr_metrics['metrics']

    return metrics

def get_cbas(url="", user="", passwrd="", nodes=[]):
    '''Entry point for getting the metrics for the analytics nodes'''
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])

    if len(nodes) == 0:

        if len(cluster_values['serviceNodes']['cbas']) > 0:
            cbas_metrics = cb_analytics._get_cbas_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['cbas'], cluster_values['clusterName'])

            metrics = cbas_metrics['metrics']
    else:
        cbas_metrics = cb_analytics._get_cbas_metrics(
            user,
            passwrd,
            nodes, cluster_values['clusterName'])
        metrics = cbas_metrics['metrics']

    return metrics

def get_fts(url="", user="", passwrd="", nodes=[], buckets=[]):
    '''Entry point for getting the metrics for the fts nodes'''
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])

    if len(nodes) == 0:

        if len(buckets) == 0:
            if len(cluster_values['serviceNodes']['kv']) > 0:
                bucket_metrics = cb_bucket._get_bucket_metrics(user,
                                                     passwrd,
                                                     cluster_values['serviceNodes']['kv'],
                                                     cluster_values['clusterName'])
        else:
            bucket_metrics = {"buckets": buckets}

        if len(cluster_values['serviceNodes']['fts']) > 0:
            fts_metrics = cb_fts._get_fts_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['fts'],
                bucket_metrics['buckets'], cluster_values['clusterName'])

            metrics = fts_metrics['metrics']
    else:
        if len(buckets) == 0:
            bucket_metrics = cb_bucket._get_bucket_metrics(
                user, passwrd, nodes, cluster_values['clusterName'])
        else:
            bucket_metrics = {"buckets": buckets}

        fts_metrics = cb_fts._get_fts_metrics(
            user,
            passwrd,
            nodes,
            bucket_metrics['buckets'], cluster_values['clusterName'])

        metrics = fts_metrics['metrics']

    return(metrics)

def get_metrics(url="10.112.192.101", user="Administrator", passwrd="password"):
    '''This is the entry point for this script. Gets each type of metric and
    combines them to present'''
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    metrics = cluster_values['metrics']
    index_buckets = cb_bucket._get_index_buckets(url, user, passwrd)

    node_metrics = cb_nodes._get_node_metrics(
        user, passwrd, cluster_values['nodeList'], cluster_values['clusterName'])
    metrics = metrics + node_metrics['metrics']

    system_metrics = cb_system._get_system_metrics(
        user, passwrd, cluster_values['nodeList'], cluster_values['clusterName'])
    metrics = metrics + system_metrics['metrics']

    if len(cluster_values['serviceNodes']['kv']) > 0:
        bucket_metrics = cb_bucket._get_bucket_metrics(
            user, passwrd, cluster_values['serviceNodes']['kv'], cluster_values['clusterName'])
        metrics = metrics + bucket_metrics['metrics']

        xdcr_metrics = cb_xdcr._get_xdcr_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['kv'],
            bucket_metrics['buckets'], cluster_values['clusterName'])
        metrics = metrics + xdcr_metrics['metrics']

    if len(cluster_values['serviceNodes']['index']) > 0 and index_buckets > 0:
        index_metrics = cb_index._get_index_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['index'],
            index_buckets, cluster_values['clusterName'])
        metrics = metrics + index_metrics['metrics']

    if len(cluster_values['serviceNodes']['n1ql']) > 0:
        query_metrics = cb_query._get_query_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['n1ql'], cluster_values['clusterName'])
        metrics = metrics + query_metrics['metrics']

    if len(cluster_values['serviceNodes']['eventing']) > 0:
        eventing_metrics = cb_eventing._get_eventing_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['eventing'], cluster_values['clusterName'])
        metrics = metrics + eventing_metrics['metrics']

    if len(cluster_values['serviceNodes']['fts']) > 0:
        fts_metrics = cb_fts._get_fts_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['fts'],
            bucket_metrics['buckets'], cluster_values['clusterName'])
        metrics = metrics + fts_metrics['metrics']

    if len(cluster_values['serviceNodes']['cbas']) > 0:
        cbas_metrics = cb_analytics._get_cbas_metrics(
            user,
            passwrd,
            cluster_values['serviceNodes']['cbas'], cluster_values['clusterName'])
        metrics = metrics + cbas_metrics['metrics']

    return(metrics)

if __name__ == "__main__":
    URL = "10.112.192.101"
    USER = "Administrator"
    PASSWD = "password"

    get_metrics(URL, USER, PASSWD)
    # print(cb_cluster._get_cluster(URL, USER, PASSWD, []))