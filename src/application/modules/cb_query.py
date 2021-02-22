import re
import hashlib
import sys

if sys.version_info[0] == 3:
    from .cb_utilities import *
    from . import cb_cluster
    import urllib.request
    from urllib.parse import urlencode
else:
    from cb_utilities import *
    import cb_cluster
    import urllib
    from urllib import urlencode

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "query"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},
                        {"variable":"slow_queries","type":"default","name":"slow_queries","value": True},
                        {"variable":"result_set","type":"int","name":"num_samples","value":60}]
        self.comment = '''This is the method used to access FTS metrics'''
        self.service_identifier = "n1ql"
        self.inputs = [{"value":"user"},
                        {"value":"passwrd"},
                        {"value":"cluster_values['serviceNodes']['{}']".format(self.service_identifier)},
                        {"value":"cluster_values['clusterName']"},
                        {"value":"result_set"}]
        self.exclude = False


def run(url="", user="", passwrd="", nodes=[], slow_queries=True, num_samples = 60, result_set=60):
    '''Entry point for getting the metrics for the query nodes'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if num_samples != 60:
        result_set = num_samples
    if len(nodes) == 0:
        if len(cluster_values['serviceNodes']['n1ql']) > 0:
            # get the metrics from the query service for each of the n1ql nodes
            query_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['n1ql'], cluster_values['clusterName'],
                slow_queries,
                result_set)
            metrics = query_metrics['metrics']
    else:
        # get the metrics from the query service for each of the n1ql nodes
        query_metrics = _get_metrics(
            user,
            passwrd,
            nodes, cluster_values['clusterName'],
            slow_queries,
            result_set)
        metrics = query_metrics['metrics']
    return metrics

def _get_metrics(user, passwrd, node_list, cluster_name="", slow_queries=True, result_set=60):
    '''Gets the metrics for the query nodes'''
    # first get the system:completed_request entries for the past minute
    query_info = {}
    query_info['metrics'] = []

    auth = basic_authorization(user, passwrd)
    sample_list = get_sample_list(result_set)
    if slow_queries:
        query_info['metrics'] = _get_completed_query_metrics(auth, node_list, cluster_name)

    for node in node_list:
        node_hostname = node.split(":")[0]
        try:
            _query_url = "http://{}:8091/pools/default/buckets/@query/nodes/{}:8091/stats".format(
                node_hostname, node_hostname)
            q_json = rest_request(auth, _query_url)
            for record in q_json['op']['samples']:
                samples_count = len(q_json['op']['samples'][record])
                if record != "timestamp":
                    # if the sample list value is greater than the samples count, just use the last sample
                    if samples_count < sample_list[0]:
                        query_info['metrics'].append(
                            "{} {{cluster=\"{}\", node=\"{}\", "
                            "type=\"query\"}} {} {}".format(
                                record,
                                cluster_name,
                                node_hostname,
                                q_json['op']['samples'][record][samples_count - 1],
                                q_json['op']['samples']['timestamp'][samples_count - 1]
                            )
                        )
                    else:
                        for idx, datapoint in enumerate(q_json['op']['samples'][record]):
                            if idx in sample_list:
                                query_info['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "type=\"query\"}} {} {}".format(
                                        record,
                                        cluster_name,
                                        node_hostname,
                                        datapoint,
                                        q_json['op']['samples']['timestamp'][idx]
                                    )
                                )

        except Exception as e:
            print("query base: " + str(e))
    return query_info

def _get_completed_query_metrics(auth, node_list, cluster_name=""):
    '''Queries system:completed_requests on the specific query node'''
    metrics = []

    # n1ql statement to find all of the the completed requests from the past 60 seconds (if any)
    n1ql_stmt = """SELECT IFMISSING(preparedText, statement) as statement,
        service_time_ms, elapsed_time_ms, queue_time_ms, request_time_ms,
        resultCount AS result_count, resultSize AS result_size, query_selectivity_percent,
        scan_results, fetches
    FROM system:completed_requests
    LET request_time_ms = STR_TO_MILLIS(STR_TO_UTC(REPLACE(REGEX_REPLACE(REPLACE(REPLACE(REGEX_REPLACE(requestTime, " [A-Z]{3}$", ''), ' -', '-'), ' +', '+'), '00$', ':00'), ' ', 'T'))),
        service_time_ms = ROUND(STR_TO_DURATION(serviceTime) / 1e6),
        elapsed_time_ms = ROUND(STR_TO_DURATION(elapsedTime) / 1e6),
        queue_time_ms = ROUND(
          (STR_TO_DURATION(elapsedTime) - STR_TO_DURATION(serviceTime)) / 1e6
        , 3),
        query_selectivity_percent = ROUND(IFNULL(
          (
            resultCount /
            IFMISSING(phaseCounts.`indexScan`, 0)
          ) * 100,
        0), 2),
        scan_results = IFMISSING(phaseCounts.`indexScan`, 0),
        fetches = IFMISSING(phaseCounts.`fetch`, 0)
    WHERE node = NODE_NAME()
        AND UPPER(IFMISSING(preparedText, statement)) NOT LIKE 'INFER %'
        AND UPPER(IFMISSING(preparedText, statement)) NOT LIKE 'ADVISE %'
        AND UPPER(IFMISSING(preparedText, statement)) NOT LIKE '% INDEX%'
        AND UPPER(IFMISSING(preparedText, statement)) NOT LIKE '% SYSTEM:%'
        AND request_time_ms >= ROUND(STR_TO_MILLIS(NOW_UTC()), 0) - 60000"""

    # strip new lines and convert two or more spaces to a single space
    # and then url encode the statement
    n1ql_stmt = urlencode({ "statement": re.sub(" +", " ", n1ql_stmt.strip("\r\n")) })

    for node in node_list:
        node_hostname = node.split(":")[0]
        try:
            _query_url = "http://{}:8093/query/service?{}".format(
                node_hostname,
                n1ql_stmt
            )
            q_json = rest_request(auth, _query_url)
            for record in q_json['results']:
                statement = record['statement'].replace('"','\\"').replace('\n', ' ')
                # generate a hash of the statement so that if the user wants the statement
                # can be disregarded and the hash can still be used to group repeat statements
                statement_signature = hashlib.sha1(statement).hexdigest()
                # stat: service_time_ms
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_service_time_ms",
                        cluster_name,
                        node_hostname,
                        statement_signature,
                        statement,
                        record['service_time_ms'],
                        record['request_time_ms']
                    )
                )
                # stat: queue_time_ms
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_queue_time_ms",
                        cluster_name,
                        node_hostname,
                        statement_signature,
                        statement,
                        record['queue_time_ms'],
                        record['request_time_ms']
                    )
                )
                # stat: elapsed_time_ms
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_elapsed_time_ms",
                        cluster_name,
                        node_hostname,
                        statement_signature,
                        statement,
                        record['elapsed_time_ms'],
                        record['request_time_ms']
                    )
                )
                # stat: result_count
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_result_count",
                        cluster_name,
                        node_hostname,
                        statement_signature,
                        statement,
                        record['result_count'],
                        record['request_time_ms']
                    )
                )
                # stat: result_size_bytes
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_result_size_bytes",
                        cluster_name,
                        node_hostname,
                        statement_signature,
                        statement,
                        record['result_size'],
                        record['request_time_ms']
                    )
                )
                # stat: query_selectivity_percent
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_query_selectivity_percent",
                        cluster_name,
                        node_hostname,
                        statement_signature,
                        statement,
                        record['query_selectivity_percent'],
                        record['request_time_ms']
                    )
                )
                # stat: scan_results
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_scan_results",
                        cluster_name,
                        node_hostname,
                        statement_signature,
                        statement,
                        record['scan_results'],
                        record['request_time_ms']
                    )
                )
                # stat: fetches
                metrics.append(
                    "{} {{cluster=\"{}\", node=\"{}\", "
                    "signature=\"{}\", "
                    "statement=\"{}\", "
                    "type=\"completed-request\"}} {} {}".format(
                        "completed_request_fetches",
                        cluster_name,
                        node_hostname,
                        statement_signature,
                        statement,
                        record['fetches'],
                        record['request_time_ms']
                    )
                )
        except Exception as e:
            print("completed query: " + str(e))
    return metrics
